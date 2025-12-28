import os
import subprocess
import json
import time
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Assuming these imports are available from your multi-agent system structure
# You would need to adapt these to your actual messaging and logging implementations
# from src.comms.multi_agent_messenger import MultiAgentMessenger
# from src.logging.structured_logger import ProductionLogger

# Placeholder for MessagingSystem and ProductionLogger if not yet implemented or for standalone testing
class MockMessenger:
    def __init__(self, agent_id):
        self.agent_id = agent_id
    def send_unicast(self, to_agent, message):
        print(f"[{self.agent_id}] Mock sending unicast to {to_agent}: {message.get('subject', '')}")
    def send_broadcast(self, message):
        print(f"[{self.agent_id}] Mock sending broadcast: {message.get('subject', '')}")
    def start_listening(self, callback):
        print(f"[{self.agent_id}] Mock listening started. Will not receive real messages.")
        # In a real system, this would run a thread to listen for messages
        # For this mock, we'll simulate a blocking wait for simplicity in example
        print(f"[{self.agent_id}] MockMessenger: Listening for messages...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"[{self.agent_id}] MockMessenger: Stopped listening.")

class MockLogger:
    def __init__(self, agent_id):
        self.agent_id = agent_id
    def info(self, event, **kwargs):
        print(f"[LOG][{self.agent_id}][INFO] {event}: {kwargs}")
    def error(self, event, **kwargs):
        print(f"[LOG][{self.agent_id}][ERROR] {event}: {kwargs}")
    def critical(self, event, **kwargs):
        print(f"[LOG][{self.agent_id}][CRITICAL] {event}: {kwargs}")


# --- Configuration Loading ---
CONFIG_FILE_PATH = Path("C:/Dev/llm-research/deepseek-ocr/models/config.json")
MANIFEST_FILE_PATH = Path("C:/Dev/llm-research/deepseek-ocr/models/manifest.json")

def load_config():
    if not CONFIG_FILE_PATH.exists():
        raise FileNotFoundError(f"Config file missing: {CONFIG_FILE_PATH}")
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_manifest():
    if not MANIFEST_FILE_PATH.exists():
        return {"models": {}} # Return empty manifest if not exists
    with open(MANIFEST_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_manifest(manifest_data):
    MANIFEST_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=4)

CONFIG = load_config()

class OCRAgent:
    """
    Agent responsible for orchestrating local DeepSeek-OCR processing.
    Listens for OCR requests and returns processed text.
    """

    def __init__(self, agent_id: str = "ocr_agent"):
        self.agent_id = agent_id
        
        # Initialize messaging and logging (use mocks if actual not available)
        try:
            from src.comms.multi_agent_messenger import MultiAgentMessenger
            self.messenger = MultiAgentMessenger(self.agent_id, None) # Registry would be passed
        except ImportError:
            self.messenger = MockMessenger(self.agent_id)
            # print("WARNING: Using MockMessenger. Real messaging system not found.") # Already printed by MockMessenger
        
        try:
            from src.logging.structured_logger import ProductionLogger
            self.logger = ProductionLogger(self.agent_id)
        except ImportError:
            self.logger = MockLogger(self.agent_id)
            print("WARNING: Using MockLogger. Real logging system not found.")

        self.ocr_script_path = Path("C:/Dev/llm-research/deepseek-ocr/scripts/run_ocr.py")
        self.ocr_input_dir = Path("C:/Dev/llm-research/deepseek-ocr/data/input")
        self.ocr_output_dir = Path("C:/Dev/llm-research/deepseek-ocr/data/output")
        self.env_script_path = Path("C:/Dev/llm-research/deepseek-ocr/scripts/environment.ps1")
        
        # Ensure OCR data directories exist
        self.ocr_input_dir.mkdir(parents=True, exist_ok=True)
        self.ocr_output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("OCRAgent initialized", 
                         ocr_script=str(self.ocr_script_path),
                         ocr_input=str(self.ocr_input_dir),
                         ocr_output=str(self.ocr_output_dir))
        
        # Load manifest to get model info
        self.manifest = load_manifest()
        
    def _run_powershell_script(self, script_path: Path, args: list = []):
        command = [
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)
        ] + args
        
        self.logger.info("Running PowerShell script", command=" ".join(command))
        try:
            process = subprocess.run(command, capture_output=True, text=True, check=True)
            self.logger.info("PowerShell script Stdout", stdout=process.stdout)
            if process.stderr:
                self.logger.warning("PowerShell script Stderr", stderr=process.stderr)
            return True, process.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error("PowerShell script failed", error=str(e), stdout=e.stdout, stderr=e.stderr)
            return False, e.stderr
        except Exception as e:
            self.logger.error("Error executing PowerShell script", error=str(e))
            return False, str(e)

    def pre_flight_checks(self):
        """
        Performs essential checks before the OCR agent starts listening.
        Addresses Codex Amendment A3 (Environment & model lifecycle automation).
        """
        self.logger.info("Running pre-flight checks for OCRAgent startup...")

        # 1. Check Python environment setup
        self.logger.info("Verifying Python virtual environment and dependencies...")
        success, output = self._run_powershell_script(self.env_script_path, ["-CheckOnly", "True"])
        if not success:
            self.logger.critical("DeepSeek-OCR environment not properly set up. Please run deepseek-ocr/scripts/environment.ps1 without -CheckOnly flag. Exiting.")
            sys.exit(1)
        self.logger.info("Python environment checks passed.")

        # 2. Check model weights presence (fp16 and default quantized)
        self.logger.info("Verifying DeepSeek-OCR model weights presence...")
        required_models = [CONFIG["models"]["fp16"]]
        default_quant = CONFIG["models"].get(CONFIG["default_quantization"])
        if default_quant and default_quant != required_models[0]:
            required_models.append(default_quant)

        missing_models = []
        for model_config in required_models:
            model_path = Path(model_config["model_path"])
            adapter_path = Path(model_config["adapter_path"])
            
            # Simple check: model_path should be a directory with some content
            if not model_path.is_dir() or not any(model_path.iterdir()):
                missing_models.append(model_config["quantization_level"] + " base model")
            if adapter_path and (not adapter_path.is_dir() or not any(adapter_path.iterdir())):
                missing_models.append(model_config["quantization_level"] + " adapter")
        
        if missing_models:
            self.logger.critical(f"Missing DeepSeek-OCR model weights/adapters: {', '.join(missing_models)}. Please run deepseek-ocr/scripts/environment.ps1 to download models. Exiting.")
            sys.exit(1)
        self.logger.info("DeepSeek-OCR model weights checks passed.")

        # 3. Check CUDA availability (if device is cuda)
        if "cuda" in self.get_ocr_device():
            self.logger.info("Verifying CUDA availability...")
            if not torch.cuda.is_available():
                self.logger.critical("CUDA not available but 'cuda' device specified. Please check CUDA installation. Exiting.")
                sys.exit(1)
            dummy_tensor = torch.ones(1).to(self.get_ocr_device()) # Test if it can move to GPU
            self.logger.info(f"CUDA available. Device: {self.get_ocr_device()}")
        
        self.logger.info("Pre-flight checks completed successfully. OCRAgent is ready.")
        return True

    def get_ocr_device(self):
        """Determine OCR device based on CUDA availability."""
        if torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"

    def _handle_ocr_request(self, message: dict):
        """
        Processes an incoming OCR request.
        Message content should contain 'file_path' of the PDF/image.
        """
        from_agent = message.get('from', 'unknown')
        request_id = message.get('msg_id', 'no_id')
        input_file_path_str = message.get('content', {}).get('file_path')
        quantization_level = message.get('content', {}).get('quantization_level', CONFIG["default_quantization"])

        self.logger.info("Received OCR request", from_agent=from_agent, 
                         request_id=request_id, file_path=input_file_path_str, 
                         quant_level=quantization_level)

        if not input_file_path_str:
            self.logger.error("OCR request missing file_path", from_agent=from_agent, request_id=request_id)
            self.messenger.send_unicast(from_agent, {
                "subject": f"OCR_ERROR: Missing file_path for request {request_id}",
                "body": "Your OCR request was missing the 'file_path' argument in its content."
            })
            return

        input_file_path = Path(input_file_path_str)
        if not input_file_path.exists():
            self.logger.error("OCR input file not found", from_agent=from_agent, 
                             request_id=request_id, file_path=str(input_file_path))
            self.messenger.send_unicast(from_agent, {
                "subject": f"OCR_ERROR: File not found for request {request_id}",
                "body": f"The requested file '{input_file_path_str}' does not exist on the system."
            })
            return

        # Copy file to OCR input directory (for isolated processing)
        target_input_file = self.ocr_input_dir / input_file_path.name
        try:
            shutil.copy(input_file_path, target_input_file)
            self.logger.info("File copied for OCR", original=str(input_file_path), target=str(target_input_file))
        except Exception as e:
            self.logger.error("Failed to copy file for OCR", from_agent=from_agent, 
                             request_id=request_id, file_path=str(input_file_path), error=str(e))
            self.messenger.send_unicast(from_agent, {
                "subject": f"OCR_ERROR: File copy failed for request {request_id}",
                "body": f"Failed to copy '{input_file_path_str}' for OCR processing: {e}"
            })
            return

        # Get model paths based on quantization level
        try:
            model_path_str, adapter_path_str, actual_quant_level = CONFIG["models"].get(quantization_level)["model_path"], CONFIG["models"].get(quantization_level)["adapter_path"], quantization_level # Simplified for now, will refine get_model_paths
            # Refined path retrieval
            # model_path_str, adapter_path_str, actual_quant_level = get_model_paths(quantization_level)
        except Exception as e:
            self.logger.error(f"Invalid quantization level '{quantization_level}' or config error: {e}", exc_info=True)
            self.messenger.send_unicast(from_agent, {
                "subject": f"OCR_ERROR: Invalid quantization level for request {request_id}",
                "body": f"The requested quantization level '{quantization_level}' is invalid or missing in config.json. Error: {e}"
            })
            return


        # Execute OCR script
        try:
            self.logger.info("Executing OCR script", input_file=str(target_input_file), quant_level=actual_quant_level)
            command = [
                "powershell.exe", "-NoProfile", "-Command",
                str(self.ocr_script_path),
                "--input_path", str(target_input_file),
                "--output_dir", str(self.ocr_output_dir),
                "--quantization_level", actual_quant_level,
                "--device", self.get_ocr_device() 
            ]
            
            # Using Popen for better control and non-blocking if needed, but for simplicity, wait.
            process = subprocess.run(command, capture_output=True, text=True, check=True)
            
            self.logger.info("OCR script executed", stdout=process.stdout, stderr=process.stderr)
            
            # Read OCR results (assuming it generates a summary.json)
            ocr_summary_path = self.ocr_output_dir / "ocr_summary.json"
            if ocr_summary_path.exists():
                with open(ocr_summary_path, "r", encoding="utf-8") as f:
                    ocr_results = json.load(f)
                
                # Extract text for the original file, or all pages if PDF
                extracted_texts = []
                for res in ocr_results:
                    if res.get("status") == "success":
                        # Make sure output_text_path exists before trying to read
                        if Path(res["output_text_path"]).exists():
                            with open(res["output_text_path"], "r", encoding="utf-8") as f_txt:
                                extracted_texts.append(f_txt.read())
                        else:
                            self.logger.warning(f"Output text file not found for {res.get('image_path')}, skipping.")
                
                full_extracted_text = "\n\n" + "=" * 10 + " Page Break " + "=" * 10 + "\n\n".join(extracted_texts) if extracted_texts else "No text extracted."

                # Send results back
                self.messenger.send_unicast(from_agent, {
                    "subject": f"OCR_RESULT for request {request_id}",
                    "body": "OCR processing complete.",
                    "original_file": input_file_path_str,
                    "ocr_output_text": full_extracted_text, # Potentially large, consider saving to file and sending path
                    "ocr_summary": ocr_results,
                    "quantization_level_used": actual_quant_level
                })
                self.logger.info("OCR result sent", request_id=request_id, output_len=len(full_extracted_text))
            else:
                self.logger.error("OCR summary file not found", from_agent=from_agent, request_id=request_id)
                self.messenger.send_unicast(from_agent, {
                    "subject": f"OCR_ERROR: No OCR output for request {request_id}",
                    "body": "OCR script ran but did not produce an 'ocr_summary.json' file. Check script logs."
                })

        except subprocess.CalledProcessError as e:
            self.logger.error("OCR script failed", from_agent=from_agent, 
                             request_id=request_id, error=str(e), stdout=e.stdout, stderr=e.stderr)
            self.messenger.send_unicast(from_agent, {
                "subject": f"OCR_ERROR: Script execution failed for request {request_id}",
                "body": f"DeepSeek-OCR script failed to execute. Stderr: {e.stderr}. Check deepseek-ocr/data/output for logs."
            })
        except Exception as e:
            self.logger.error("An unexpected error occurred during OCR processing", from_agent=from_agent, 
                             request_id=request_id, error=str(e), exc_info=True)
            self.messenger.send_unicast(from_agent, {
                "subject": f"OCR_ERROR: Unexpected error for request {request_id}",
                "body": f"An unexpected error occurred during OCR processing: {e}. Check agent logs."
            })
        finally:
            # Clean up copied input file
            if target_input_file.exists():
                os.remove(target_input_file)
                self.logger.info("Cleaned up temporary input file", file=str(target_input_file))

    def start(self):
        """Starts the OCR agent, listening for requests."""
        # Perform pre-flight checks before starting listener
        if not self.pre_flight_checks():
            self.logger.critical("Pre-flight checks failed. OCRAgent cannot start.")
            sys.exit(1) # Exit if pre-flight checks fail

        self.logger.info("OCRAgent starting to listen for messages.")
        # This callback needs to be adapted to your actual messenger's message structure
        # Assuming the messenger calls this method directly with the full message dict
        self.messenger.start_listening(self._handle_ocr_request)
        print(f"OCRAgent '{self.agent_id}' is running and listening for OCR requests...")
        # Keep the agent alive. In a real system, this would be a more robust event loop
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("OCRAgent received KeyboardInterrupt. Shutting down.")
            print(f"OCRAgent '{self.agent_id}' shutting down.")

if __name__ == "__main__":
    # Example of how to run the agent
    # In a real setup, this would be integrated into the main multi-agent orchestration
    
    # First, make sure your DeepSeek-OCR environment is set up:
    # 1. Run deepseek-ocr/scripts/environment.ps1
    # 2. Ensure DeepSeek-OCR models are downloaded
    # 3. Ensure PyMuPDF is installed for PDF processing in the run_ocr.py script.
    #    pip install PyMuPDF (within the deepseek-ocr venv)

    ocr_agent = OCRAgent()
    ocr_agent.start()

    # To test manually (assuming MockMessenger):
    # ocra_agent.messenger.send_unicast("ocr_agent", {
    #     "subject": "OCR_REQUEST",
    #     "content": {"file_path": "C:\\Dev\\llm-research\\ACE\\2510.04618v1.pdf", "quantization_level": "Q5_K_M"},
    #     "from": "test_requester",
    #     "msg_id": "test_123"
    # })
    # time.sleep(10) # Give it time to process