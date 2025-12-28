# PowerShell script to benchmark DeepSeek-OCR quantizations
# This script runs OCR on samples in data/eval using both fp16 and Q5_K_M models.
# It captures execution time and (if available via external tools) VRAM usage.
# CER calculation would require ground truth text, which we simulate/placeholder here.

$EVAL_DIR = "C:\Dev\llm-research\deepseek-ocr\data\eval"
$OUTPUT_DIR = "C:\Dev\llm-research\deepseek-ocr\data\benchmarks"
$PYTHON_EXE = "C:\Dev\llm-research\deepseek-ocr\.venv\Scripts\python.exe"
$RUN_OCR_SCRIPT = "C:\Dev\llm-research\deepseek-ocr\scripts\run_ocr.py"

# Ensure output directory exists
if (-not (Test-Path $OUTPUT_DIR)) {
    mkdir $OUTPUT_DIR | Out-Null
}

$reportPath = "$OUTPUT_DIR\quant_report_$(Get-Date -Format 'yyyyMMdd_HHmm').json"
$results = @()

# Check if eval directory has files
$evalFiles = Get-ChildItem -Path $EVAL_DIR -Include *.pdf, *.png, *.jpg -Recurse
if ($evalFiles.Count -eq 0) {
    Write-Host "No evaluation files found in $EVAL_DIR. Please add some PDFs or images." -ForegroundColor Yellow
    exit
}

$quantizationLevels = @("fp16", "Q5_K_M")

foreach ($file in $evalFiles) {
    Write-Host "Benchmarking file: $($file.Name)" -ForegroundColor Cyan
    
    foreach ($quant in $quantizationLevels) {
        Write-Host "  Running with quantization: $quant" -ForegroundColor Green
        
        $startTime = Get-Date
        
        # Run OCR script
        # Note: To capture VRAM, one would typically wrap this in a python script using pynvml
        # or run nvidia-smi in parallel. Here we focus on wall-clock time.
        $process = Start-Process -FilePath $PYTHON_EXE -ArgumentList "$RUN_OCR_SCRIPT --input_path `"$($file.FullName)`" --output_dir `"$OUTPUT_DIR\$quant`" --quantization_level $quant" -PassThru -Wait -NoNewWindow
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        $exitCode = $process.ExitCode
        
        if ($exitCode -eq 0) {
            Write-Host "    Success! Duration: $duration seconds" -ForegroundColor Gray
            
            $resultEntry = [PSCustomObject]@{
                file = $file.Name
                quantization = $quant
                duration_seconds = $duration
                timestamp = $endTime.ToString("o")
                status = "success"
            }
            $results += $resultEntry
        } else {
            Write-Host "    Failed! Exit code: $exitCode" -ForegroundColor Red
             $resultEntry = [PSCustomObject]@{
                file = $file.Name
                quantization = $quant
                duration_seconds = $null
                timestamp = $endTime.ToString("o")
                status = "failed"
                exit_code = $exitCode
            }
            $results += $resultEntry
        }
    }
}

# Save report
$results | ConvertTo-Json -Depth 4 | Set-Content -Path $reportPath
Write-Host "Benchmark complete. Report saved to $reportPath" -ForegroundColor Green

