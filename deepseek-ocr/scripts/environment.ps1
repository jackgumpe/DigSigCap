# PowerShell script to set up DeepSeek-OCR environment
# This script will:
# 1. Create or verify a Python virtual environment
# 2. Install necessary Python packages
# 3. Perform pre-flight checks for CUDA and Hugging Face authentication
# 4. Conditionally download DeepSeek-OCR model weights and adapters

# --- Configuration ---
$VENV_PATH = "C:\Dev\llm-research\deepseek-ocr\.venv"
$PYTHON_EXE = "$VENV_PATH\Scripts\python.exe"
$PIP_EXE = "$VENV_PATH\Scripts\pip.exe"
$HUGGINGFACE_CLI_EXE = "$VENV_PATH\Scripts\huggingface-cli.exe"

$MODEL_BASE_NAME = "deepseek-ai/DeepSeek-OCR"
$MODEL_FP16_DIR = "C:\Dev\llm-research\deepseek-ocr\models\fp16\$MODEL_BASE_NAME"
$ADAPTER_FP16_DIR = "C:\Dev\llm-research\deepseek-ocr\models\fp16\deepseek-ai\DeepSeek-OCR-Large-Adapter"

# Quantized model paths (these would be created by conversion later)
$MODEL_Q5KM_DIR = "C:\Dev\llm-research\deepseek-ocr\models\quantized\$MODEL_BASE_NAME-Q5K_M"
$ADAPTER_Q5KM_DIR = "C:\Dev\llm-research\deepseek-ocr\models\quantized\deepseek-ai\DeepSeek-OCR-Large-Adapter-Q5K_M"

$MODEL_MANIFEST_PATH = "C:\Dev\llm-research\deepseek-ocr\models\manifest.json"

# --- Helper Functions ---
function Write-Log {
    param (
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Color = "White"
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$Timestamp][$Level] $Message" -ForegroundColor $Color
}

function Check-Command {
    param (
        [string]$CommandName
    )
    return (Get-Command $CommandName -ErrorAction SilentlyContinue) -ne $null
}

function Check-Python {
    Write-Log "Checking Python installation..."
    if (-not (Check-Command python)) {
        Write-Log "Python not found. Please install Python 3.9+ (add to PATH)." -ForegroundColor Red -Level ERROR
        Write-Log "Download from: https://www.python.org/downloads/" -ForegroundColor Red
        exit 1
    }
    Write-Log "Python found." -ForegroundColor Green
}

function Check-CUDA {
    Write-Log "Checking CUDA installation and compatibility..."
    # A basic check. A more thorough check would involve PyTorch's cuda.is_available()
    if (-not (Check-Command nvidia-smi)) {
        Write-Log "nvidia-smi not found. CUDA drivers might not be installed or in PATH." -ForegroundColor Yellow -Level WARN
        Write-Log "Proceeding, but GPU inference will likely fail if CUDA is required." -ForegroundColor Yellow
        return $false
    }
    
    $nvidiaSmiOutput = nvidia-smi
    if ($nvidiaSmiOutput -match "CUDA Version:\s+(\d+\.\d+)") {
        $cudaVersion = $Matches[1]
        Write-Log "CUDA found: Version $cudaVersion. Ensure PyTorch wheels match this version (e.g., cu118 for CUDA 11.8)." -ForegroundColor Green
        return $true
    } else {
        Write-Log "Could not determine CUDA version from nvidia-smi." -ForegroundColor Yellow -Level WARN
        return $false
    }
}

function Test-VenvIntegrity {
    Write-Log "Testing virtual environment integrity..."
    if (-not (Test-Path $VENV_PATH)) {
        Write-Log "Virtual environment not found. Creating a new one." -ForegroundColor Yellow
        python -m venv $VENV_PATH
        if (-not (Test-Path $PYTHON_EXE)) {
            Write-Log "Failed to create virtual environment." -ForegroundColor Red -Level ERROR
            exit 1
        }
        Write-Log "Virtual environment created." -ForegroundColor Green
        return $false # Indicate fresh venv, so dependencies must be installed
    }
    
    # Check if core packages are installed
    $required_packages = @("torch", "transformers", "pymupdf")
    $missing_packages = @()
    foreach ($pkg in $required_packages) {
        if (-not (& $PYTHON_EXE -c "import $pkg" -ErrorAction SilentlyContinue)) {
            $missing_packages += $pkg
        }
    }

    if ($missing_packages.Count -gt 0) {
        Write-Log "Virtual environment exists but missing core packages: $($missing_packages -join ', ')." -ForegroundColor Yellow -Level WARN
        Write-Log "Reinstalling dependencies." -ForegroundColor Yellow
        return $false # Indicate dependencies need reinstallation
    }
    
    Write-Log "Virtual environment exists and appears healthy." -ForegroundColor Green
    return $true
}

function Install-PythonDependencies {
    param (
        [bool]$ForceInstall = $false
    )
    if ($ForceInstall) {
        Write-Log "Forcing reinstallation of Python dependencies..." -ForegroundColor Green
    } else {
        Write-Log "Installing Python dependencies (if needed)..." -ForegroundColor Green
    }
    
    & $PIP_EXE install --upgrade pip
    
    # Check CUDA availability to determine PyTorch wheel
    $cuda_available = Check-CUDA
    if ($cuda_available) {
        Write-Log "Installing PyTorch with CUDA support." -ForegroundColor Green
        & $PIP_EXE install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 # User to verify cu118 matches their CUDA
    } else {
        Write-Log "Installing PyTorch for CPU only." -ForegroundColor Yellow
        & $PIP_EXE install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    }
    
    & $PIP_EXE install transformers tokenizers einops addict easydict accelerate optimum pymupdf huggingface_hub
    
    # flash-attn/xformers for performance if CUDA is available
    if ($cuda_available) {
        Write-Log "Attempting to install xformers for optimized attention (optional)." -ForegroundColor Green
        try {
            & $PIP_EXE install xformers # More compatible on Windows
            Write-Log "xformers installed." -ForegroundColor Green
        } catch {
            Write-Log "Failed to install xformers. DeepSeek-OCR will still work without it but may be slower. Error: $($_.Exception.Message)" -ForegroundColor Yellow -Level WARN
        }
    }

    Write-Log "Python dependencies installed." -ForegroundColor Green
}

function Check-HuggingFaceLogin {
    Write-Log "Checking Hugging Face CLI login status..."
    if (-not (Check-Command $HUGGINGFACE_CLI_EXE)) {
        Write-Log "huggingface-cli not found. Installing huggingface_hub..." -ForegroundColor Yellow
        & $PIP_EXE install huggingface_hub
    }
    
    try {
        $result = & $HUGGINGFACE_CLI_EXE whoami -ErrorAction SilentlyContinue
        if ($LASTEXITCODE -eq 0 -and $result -match "Logged in as") {
            Write-Log "Hugging Face CLI already logged in." -ForegroundColor Green
            return $true
        }
    } catch {
        # Command not found or other error
    }
    
    Write-Log "Not logged into Hugging Face CLI. Please run 'huggingface-cli login' in a new PowerShell session and follow prompts." -ForegroundColor Red -Level ERROR
    Write-Log "Model downloads might fail without authentication." -ForegroundColor Yellow
    return $false
}

function Get-FileHash {
    param (
        [string]$FilePath
    )
    if (Test-Path $FilePath) {
        $hash = (Get-FileHash $FilePath -Algorithm SHA256).Hash
        return $hash
    }
    return $null
}

function Download-ModelAssets {
    param (
        [string]$RepoId,
        [string]$TargetDir,
        [string]$FileName, # e.g., 'model.safetensors' or 'adapter_model.bin'
        [string]$ExpectedHash = $null # For verification
    )
    $FinalPath = "$TargetDir\$FileName"
    $ParentDir = Split-Path $FinalPath -Parent
    if (-not (Test-Path $ParentDir)) {
        mkdir $ParentDir | Out-Null
    }

    Write-Log "Checking for $RepoId asset at $FinalPath..."
    if (Test-Path $FinalPath) {
        if ($ExpectedHash -ne $null) {
            $CurrentHash = Get-FileHash $FinalPath
            if ($CurrentHash -eq $ExpectedHash) {
                Write-Log "Asset $FileName exists and hash matches. Skipping download." -ForegroundColor Green
                return $true
            } else {
                Write-Log "Asset $FileName exists but hash MISMATCHES. Redownloading." -ForegroundColor Yellow -Level WARN
                Remove-Item $FinalPath -Force
            }
        } else {
            Write-Log "Asset $FileName exists, but no expected hash to verify. Skipping download." -ForegroundColor Yellow
            return $true
        }
    }

    Write-Log "Downloading $RepoId asset $FileName to $ParentDir..." -ForegroundColor Green
    try {
        # Use snapshot_download with specific file pattern for efficiency
        & $PYTHON_EXE -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='$RepoId', local_dir_use_symlinks=False, local_dir='$ParentDir', allow_patterns=['$FileName'])"
        
        if (Test-Path $FinalPath) {
            Write-Log "Successfully downloaded $FileName." -ForegroundColor Green
            # Verify hash if expected hash was provided
            if ($ExpectedHash -ne $null) {
                $DownloadedHash = Get-FileHash $FinalPath
                if ($DownloadedHash -eq $ExpectedHash) {
                    Write-Log "Downloaded asset hash verified." -ForegroundColor Green
                    return $true
                } else {
                    Write-Log "Downloaded asset hash MISMATCHES. Expected: $ExpectedHash, Got: $DownloadedHash." -ForegroundColor Red -Level ERROR
                    Remove-Item $FinalPath -Force # Remove corrupted download
                    return $false
                }
            }
            return $true
        } else {
            Write-Log "Download completed but $FileName not found at $FinalPath. Check allow_patterns." -ForegroundColor Red -Level ERROR
            return $false
        }
    } catch {
        Write-Log "Error downloading $RepoId asset $FileName: $($_.Exception.Message)" -ForegroundColor Red -Level ERROR
        return $false
    }
}

function Download-DeepSeekOCRModels {
    Write-Log "Downloading DeepSeek-OCR models based on config.json..." -ForegroundColor Green
    $config = (ConvertFrom-Json (Get-Content "C:\Dev\llm-research\deepseek-ocr\models\config.json" -Raw))
    
    foreach ($key in $config.models.PSObject.Properties.Name) {
        $model_info = $config.models.$key
        Write-Log "Processing model config for quantization level: $($model_info.quantization_level)..."
        
        # Download main model checkpoint (e.g., model.safetensors)
        # This part requires a more dynamic way to determine the actual safetensors filename from HF repo.
        # For simplicity, we'll assume a common filename or require manual input.
        # For now, snapshot_download gets all safetensors, json, py files.
        $BaseModelDir = $model_info.model_path
        $AdapterModelDir = $model_info.adapter_path

        Write-Log "Downloading base model for $($model_info.quantization_level)..."
        try {
             & $PYTHON_EXE -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='$($model_info.huggingface_repo_id)', revision='main', local_dir='$BaseModelDir', allow_patterns=['*.safetensors', '*.json', '*.py', 'tokenizer*'])"
            Write-Log "Base model downloaded to $BaseModelDir" -ForegroundColor Green
        } catch {
            Write-Log "Error downloading base model for $($model_info.quantization_level): $($_.Exception.Message)" -ForegroundColor Red -Level ERROR
            return $false
        }
        
        if ($model_info.adapter_repo_id) {
            Write-Log "Downloading adapter for $($model_info.quantization_level)..."
            try {
                & $PYTHON_EXE -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='$($model_info.adapter_repo_id)', revision='main', local_dir='$AdapterModelDir', allow_patterns=['*.safetensors', '*.json', '*.py'])"
                Write-Log "Adapter downloaded to $AdapterModelDir" -ForegroundColor Green
            } catch {
                Write-Log "Error downloading adapter for $($model_info.quantization_level): $($_.Exception.Message)" -ForegroundColor Red -Level ERROR
                return $false
            }
        }
    }
    Write-Log "DeepSeek-OCR model download process completed." -ForegroundColor Green
    return $true
}


# --- Main Execution ---
Write-Log "--- DeepSeek-OCR Local Setup Script ---" -ForegroundColor Cyan

Check-Python
$venvHealthy = Test-VenvIntegrity
if (-not $venvHealthy) {
    Install-PythonDependencies -ForceInstall $true
} else {
    Install-PythonDependencies # Install/update if any new deps (e.g. pymupdf, xformers)
}

$hfLoggedIn = Check-HuggingFaceLogin
if (-not $hfLoggedIn) {
    Write-Log "Hugging Face login is REQUIRED for model downloads. Please log in manually then re-run script." -ForegroundColor Red -Level ERROR
    exit 1
}

Download-DeepSeekOCRModels

Write-Log "`n--- Setup Complete ---" -ForegroundColor Cyan
Write-Log "To use the environment in PowerShell, navigate to deepseek-ocr folder and run:" -ForegroundColor Green
Write-Log "  .venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Log "Then you can run DeepSeek-OCR scripts using 'python deepseek-ocr/scripts/run_ocr.py'" -ForegroundColor Green

# --- Create .venv\Scripts\Activate.ps1 if it doesn't exist for direct activation ---
if (-not (Test-Path "$VENV_PATH\Scripts\Activate.ps1")) {
    Set-Content -Path "$VENV_PATH\Scripts\Activate.ps1" -Value @"
# This script activates the virtual environment.
# It is intended to be sourced (e.g. '. $VENV_PATH\Scripts\Activate.ps1')

# Set Python path for this session
$env:PATH = "$VENV_PATH\Scripts;" + $env:PATH
$env:VIRTUAL_ENV = "$VENV_PATH"
Write-Host "Virtual environment activated: $VENV_PATH" -ForegroundColor Green
"@
}
