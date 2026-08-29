$ErrorActionPreference = "Stop"

$BaseUrl = "http://localhost:8000"

function Write-Step {
    param([string]$Message)

    Write-Host ""
    Write-Host "==================================================" -ForegroundColor DarkGray
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor DarkGray
}

Write-Step "1. Checking API"

$health = Invoke-RestMethod `
    -Method Get `
    -Uri "$BaseUrl/health"

Write-Host "API status:" $health.status -ForegroundColor Green


Write-Step "2. Creating temporary demo account"

$timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

$email = "demo-$timestamp@example.com"
$password = "DemoPassword123!"

$registerBody = @{
    email = $email
    password = $password
} | ConvertTo-Json

$user = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/auth/register" `
    -ContentType "application/json" `
    -Body $registerBody

Write-Host "Created user:" $user.email -ForegroundColor Green


Write-Step "3. Logging in and receiving JWT"

$loginBody = @{
    email = $email
    password = $password
} | ConvertTo-Json

$login = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/auth/login" `
    -ContentType "application/json" `
    -Body $loginBody

$token = $login.access_token

$headers = @{
    Authorization = "Bearer $token"
}

Write-Host "Authenticated successfully" -ForegroundColor Green


Write-Step "4. Creating repository"

$repositoryBody = @{
    name = "AI Codebase Intelligence Demo"
    source_url = $null
} | ConvertTo-Json

$repository = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/repositories" `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $repositoryBody

$repositoryId = $repository.id

Write-Host "Repository created with ID:" $repositoryId -ForegroundColor Green


Write-Step "5. Starting background repository indexing"

$jobBody = @{
    repository_id = $repositoryId
    path = "/workspace"
} | ConvertTo-Json

$job = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/jobs/index-repository" `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $jobBody

$jobId = $job.job_id

Write-Host "Job queued:" $jobId -ForegroundColor Yellow


Write-Step "6. Waiting for Celery indexing pipeline"

while ($true) {

    $status = Invoke-RestMethod `
        -Method Get `
        -Uri "$BaseUrl/jobs/$jobId" `
        -Headers $headers

    if ($status.status -eq "SUCCESS") {
        Write-Host "Indexing completed" -ForegroundColor Green
        break
    }

    if ($status.status -eq "FAILURE") {
        Write-Host "Indexing failed" -ForegroundColor Red
        $status.result | ConvertTo-Json -Depth 10
        exit 1
    }

    if ($status.result -and $status.result.stage) {
        Write-Host "Current stage:" $status.result.stage -ForegroundColor Yellow
    }
    else {
        Write-Host "Current status:" $status.status -ForegroundColor Yellow
    }

    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "Indexing result:" -ForegroundColor Cyan
$status.result | ConvertTo-Json -Depth 10


Write-Step "7. Asking the codebase a real question"

$question = "How does authentication work in this application?"

Write-Host "Question:" -ForegroundColor Yellow
Write-Host $question

$ragBody = @{
    repository_id = $repositoryId
    query = $question
    top_k = 5
} | ConvertTo-Json

$rag = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/rag/ask" `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $ragBody

Write-Host ""
Write-Host "AI Answer" -ForegroundColor Green
Write-Host "---------"
Write-Host $rag.answer


Write-Step "8. Showing retrieved source citations"

foreach ($citation in $rag.citations) {

    Write-Host (
        "[{0}] {1}:{2}-{3}" -f `
        $citation.id,
        $citation.path,
        $citation.start_line,
        $citation.end_line
    ) -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Retrieved chunks:" $rag.retrieved_chunks
Write-Host "Prompt tokens:" $rag.prompt_tokens
Write-Host "Completion tokens:" $rag.completion_tokens
Write-Host "Cache hit:" $rag.cache_hit


Write-Step "9. Asking the exact same question again"

$cached = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/rag/ask" `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $ragBody

Write-Host "Cache hit:" $cached.cache_hit -ForegroundColor Green

if ($cached.cache_hit -eq $true) {
    Write-Host "Redis returned the cached RAG response." -ForegroundColor Green
}
else {
    Write-Host "Expected a cache hit, but received a cache miss." -ForegroundColor Yellow
}


Write-Step "Demo complete"

Write-Host "Pipeline demonstrated:" -ForegroundColor Cyan
Write-Host "FastAPI -> PostgreSQL -> Redis -> Celery -> Ingestion"
Write-Host "-> Chunking -> Embeddings -> Pinecone"
Write-Host "-> BM25 + Semantic -> RRF -> Reranker"
Write-Host "-> Ollama RAG -> Citations -> Redis Cache"