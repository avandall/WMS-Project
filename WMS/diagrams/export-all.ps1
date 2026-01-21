# WMS Architecture Diagrams - Batch Export to PNG
# Requires: npm install -g @mermaid-js/mermaid-cli

Write-Host "🎨 Exporting WMS Architecture Diagrams to PNG..." -ForegroundColor Cyan
Write-Host ""

# Configuration - A4 optimized at 300 DPI
$width = 5000
$height = 3400
$scale = 2
$backgroundColor = "white"

# Create output directory
$outputDir = "png"
if (-Not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
    Write-Host "✅ Created output directory: $outputDir" -ForegroundColor Green
}

# List of diagrams to convert
$diagrams = @(
    @{Name="01-system-architecture"; Title="System Architecture Overview"},
    @{Name="02-document-transaction-flow"; Title="Document Transaction Flow"},
    @{Name="03-database-schema"; Title="Database Schema & Relationships"},
    @{Name="04-clean-architecture"; Title="Clean Architecture Layers"},
    @{Name="05-request-lifecycle"; Title="Request Lifecycle with Security"},
    @{Name="06-file-structure"; Title="Project File Structure"},
    @{Name="07-import-document-flow"; Title="Import Document Data Flow"},
    @{Name="08-index-performance"; Title="Database Index Performance"},
    @{Name="09-security-architecture"; Title="Security Architecture"}
)

$total = $diagrams.Count
$current = 0

foreach ($diagram in $diagrams) {
    $current++
    $inputFile = "$($diagram.Name).mmd"
    $outputFile = "$outputDir\$($diagram.Name).png"
    
    Write-Host "[$current/$total] Converting: $($diagram.Title)..." -ForegroundColor Yellow
    
    try {
        # Convert using mermaid-cli with high quality settings for A4 printing
        mmdc -i $inputFile -o $outputFile -w $width -H $height -s $scale -b $backgroundColor
        
        if (Test-Path $outputFile) {
            $fileSize = (Get-Item $outputFile).Length / 1KB
            Write-Host "  ✅ Exported: $outputFile ($([math]::Round($fileSize, 2)) KB)" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Failed to create: $outputFile" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "  ❌ Error: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Export Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Output Location: $((Get-Location).Path)\$outputDir" -ForegroundColor White
Write-Host "Total Diagrams: $total" -ForegroundColor White
Write-Host ""
Write-Host "Tips for Printing:" -ForegroundColor Cyan
Write-Host "  - Images are 5000x3400px at 2x scale (ULTRA HIGH resolution)" -ForegroundColor White
Write-Host "  - Optimized for A4 paper at 300+ DPI" -ForegroundColor White
Write-Host "  - Text is crisp and sharp, lines are thick" -ForegroundColor White
Write-Host "  - Print settings: Landscape orientation, Fit to page" -ForegroundColor White
Write-Host ""
Write-Host "Ready to print!" -ForegroundColor Green
