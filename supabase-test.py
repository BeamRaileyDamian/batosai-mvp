from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = "https://gisdypsqimhoyclwsepf.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdpc2R5cHNxaW1ob3ljbHdzZXBmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc1OTk3MTEsImV4cCI6MjA1MzE3NTcxMX0.sF2JKACjMCW1bKP2w476dTrS1TPkrilsECRfnOVatdo"
BUCKET_NAME = "presentations"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

def upload_pdf(file_path: str, storage_path: str) -> dict:
    try:
        with open(file_path, "rb") as file:
            response = supabase.storage.from_(BUCKET_NAME).upload(storage_path, file)
        return response
    except Exception as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    local_pdf_path = "data\\04.The_abstraction_the_process.pdf"  # Local file path
    bucket_storage_path = "pdfs/04.The_abstraction_the_process.pdf"  # Path in the bucket
    result = upload_pdf(local_pdf_path, bucket_storage_path)
    print(result)
