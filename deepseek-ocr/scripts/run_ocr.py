import argparse
import os
import torch
from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image
import json
import fitz  # PyMuPDF
import io
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration Loading ---
CONFIG_FILE_PATH = Path("C:/Dev/llm-research/deepseek-ocr/models/config.json")

def load_config():
    if not CONFIG_FILE_PATH.exists():
        logger.error(f"Configuration file not found: {CONFIG_FILE_PATH}. Please ensure it exists.")
        raise FileNotFoundError(f"Config file missing: {CONFIG_FILE_PATH}")
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG = load_config()

def get_model_paths(quantization_level):
    model_config = CONFIG["models"].get(quantization_level)
    if not model_config:
        logger.warning(f"Quantization level '{quantization_level}' not found in config.json. Falling back to default.")
        model_config = CONFIG["models"].get(CONFIG["default_quantization"]) # Fallback to default quantized
        if not model_config: # If default is also missing, try fp16 as ultimate fallback
            logger.warning(f"Default quantization level '{CONFIG['default_quantization']}' not found. Falling back to fp16.")
            model_config = CONFIG["models"]["fp16"]
    
    if not model_config:
        logger.error("No valid model configuration found for any level, including fp16 fallback.")
        raise ValueError("No valid model configuration to load.")

    return model_config["model_path"], model_config["adapter_path"], model_config["quantization_level"]

# --- OCR Functions ---
def run_deepseek_ocr(image_paths, output_dir, model_path_str, adapter_path_str, device="cuda"):
    """
    Runs DeepSeek-OCR inference on a list of image paths.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Convert paths to Path objects for consistency
    model_path = Path(model_path_str)
    adapter_path = Path(adapter_path_str)

    processor = None
    model = None
    
    try:
        logger.info(f"Loading processor from {model_path}")
        processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
        logger.info(f"Loading model from {model_path}")
        model = AutoModelForVision2Seq.from_pretrained(model_path, trust_remote_code=True).to(device)
        
        # Load adapter if provided and exists
        if adapter_path and adapter_path.exists():
            try:
                model.load_adapter(adapter_path)
                logger.info(f"Successfully loaded adapter from {adapter_path}")
            except Exception as e:
                logger.error(f"Warning: Could not load adapter from {adapter_path}. Proceeding without adapter. Error: {e}", exc_info=True)
        else:
            logger.info("No adapter path provided or adapter not found, proceeding without adapter.")

    except Exception as e:
        logger.critical(f"Failed to load DeepSeek-OCR model or processor from {model_path}. Error: {e}", exc_info=True)
        raise RuntimeError(f"Model loading failed: {e}")
    
    results = []
    for img_path in image_paths:
        try:
            image = Image.open(img_path).convert("RGB")
            # Currently only supports single image in a batch
            pixel_values = processor(images=image, return_tensors="pt").pixel_values
            
            with torch.no_grad():
                generated_ids = model.generate(
                    pixel_values.to(device),
                    max_new_tokens=1024, # Max tokens for output
                    do_sample=False,
                )
            generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            output_filepath = os.path.join(output_dir, os.path.basename(img_path) + ".txt")
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(generated_text)
            
            results.append({
                "image_path": img_path,
                "output_text_path": output_filepath,
                "extracted_text_preview": generated_text[:200], # Preview to save space in summary
                "status": "success"
            })
            logger.info(f"OCR successful for {img_path}. Output saved to {output_filepath}")
        except Exception as e:
            results.append({
                "image_path": img_path,
                "status": "error",
                "message": str(e)
            })
            logger.error(f"Error processing {img_path}: {e}", exc_info=True)
    
    return results

def process_pdf_for_ocr(pdf_path, image_output_dir, dpi=300):
    """
    Extracts images from each page of a PDF and saves them to a directory.
    Returns a list of paths to the saved images.
    """
    if not os.path.exists(image_output_dir):
        os.makedirs(image_output_dir)

    image_paths = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
            
            img_filename = f"{Path(pdf_path).stem}_page_{page_num+1}.png"
            img_path = os.path.join(image_output_dir, img_filename)
            pix.save(img_path)
            image_paths.append(img_path)
        doc.close()
        logger.info(f"Extracted {len(image_paths)} images from {pdf_path}")
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path} for image extraction: {e}", exc_info=True)
    return image_paths

def main():
    parser = argparse.ArgumentParser(description="Run DeepSeek-OCR on PDF or image files.")
    parser.add_argument("--input_path", required=True, help="Path to input PDF or image file(s). Can be a directory.")
    parser.add_argument("--output_dir", default="C:\\Dev\\llm-research\\deepseek-ocr\\data\\output", help="Directory to save OCR results.")
    parser.add_argument("--quantization_level", default=CONFIG["default_quantization"], 
                        help=f"Quantization level to use (e.g., 'fp16', 'Q5_K_M'). Default from config.json is '{CONFIG['default_quantization']}'.")
    parser.add_argument("--device", default="cuda", help="Device to use for inference (e.g., 'cuda' or 'cpu').")
    
    args = parser.parse_args()

    model_path_str, adapter_path_str, actual_quant_level = get_model_paths(args.quantization_level)
    logger.info(f"Attempting to load model with quantization level: {actual_quant_level}")
    
    image_paths_to_ocr = []
    temp_image_dir = Path(os.path.dirname(args.output_dir)) / "temp_pdf_images"
    temp_image_dir.mkdir(parents=True, exist_ok=True) # Ensure temp dir exists

    input_path_obj = Path(args.input_path)

    if input_path_obj.is_dir():
        for file_path in input_path_obj.iterdir():
            if file_path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'):
                image_paths_to_ocr.append(str(file_path))
            elif file_path.suffix.lower() == '.pdf':
                # Process PDF pages into images temporarily
                pdf_images = process_pdf_for_ocr(str(file_path), str(temp_image_dir))
                image_paths_to_ocr.extend(pdf_images)
    elif input_path_obj.suffix.lower() == '.pdf':
        image_paths_to_ocr = process_pdf_for_ocr(str(input_path_obj), str(temp_image_dir))
    elif input_path_obj.suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'):
        image_paths_to_ocr.append(str(input_path_obj))
    else:
        logger.error(f"Unsupported input file type or path: {args.input_path}. Please provide a PDF, image file, or a directory containing them.")
        return

    if not image_paths_to_ocr:
        logger.warning("No valid image files found for OCR.")
        return

    try:
        ocr_results = run_deepseek_ocr(
            image_paths_to_ocr, 
            args.output_dir, 
            model_path_str, 
            adapter_path_str, 
            args.device
        )
    except RuntimeError as e:
        logger.critical(f"DeepSeek-OCR execution aborted due to model loading failure: {e}")
        return

    # Clean up temporary PDF images
    if temp_image_dir.exists():
        for f in temp_image_dir.iterdir():
            os.remove(f)
        os.rmdir(temp_image_dir)
        logger.info(f"Cleaned up temporary image directory: {temp_image_dir}")

    # Save overall results summary
    summary_path = Path(args.output_dir) / "ocr_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(ocr_results, f, indent=4)
    logger.info(f"OCR summary saved to {summary_path}")

if __name__ == "__main__":
    main()
