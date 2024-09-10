from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from crewai import Crew
from agent import create_web_scraper_agent
from task import create_web_scraper_task
import os

# Initialize FastAPI app
app = FastAPI()

# MongoDB connection (client)
client = MongoClient("mongodb://localhost:27017/")


# Helper function to serialize MongoDB document
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for JSON serialization
    return doc


# Function to dynamically set up MongoDB database using output_directory
def get_db(output_directory):
    db_name = output_directory.replace(os.path.sep, "_")
    return client[db_name]


# API to trigger scraping and save data in MongoDB
@app.get("/scrape/")
async def scrape_website(website_url: str, output_directory: str, content_type: str):
    try:
        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)
        get_db(output_directory)

        # Create the web scraper agent
        web_scraper_agent = create_web_scraper_agent()

        # Create the web scraper task
        web_scraper_task = create_web_scraper_task(
            website_url, content_type, output_directory, web_scraper_agent
        )

        # Create the crew and kick off the task
        crew = Crew(agents=[web_scraper_agent], tasks=[web_scraper_task], verbose=2)
        crew.kickoff()

        # Return a success response
        return JSONResponse(
            content={"message": f"Scraping completed for {website_url}"}
        )

    except Exception as e:
        # Log the error
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# API endpoint to get all or specific types of scraped content
@app.get("/all-content/")
async def get_all_content(
    output_directory: str,
    content_type: str = Query(None, pattern="^(content|images|files|audio|videos)$"),
):
    try:
        # Set up the MongoDB database using the output_directory as its name
        db = get_db(output_directory)

        # Fetch content based on the specified content_type
        if content_type:
            data = [serialize_doc(doc) for doc in db[content_type].find()]
            if not data:
                raise HTTPException(status_code=404, detail=f"No {content_type} found.")

            # Return the data for the specified content_type
            return JSONResponse(content={content_type: data})

        # Fetch all types of content (content, images, files, audio, videos)
        content = [serialize_doc(doc) for doc in db["content"].find()]
        images = [serialize_doc(doc) for doc in db["images"].find()]
        files = [serialize_doc(doc) for doc in db["files"].find()]
        audio = [serialize_doc(doc) for doc in db["audio"].find()]
        videos = [serialize_doc(doc) for doc in db["videos"].find()]

        # If all collections are empty, raise a 404 error
        if not (content or images or files or audio or videos):
            raise HTTPException(status_code=404, detail="No data found.")

        # Return all data in a structured format
        return JSONResponse(
            content={
                "content": content,
                "images": images,
                "files": files,
                "audio": audio,
                "videos": videos,
            }
        )

    except Exception as e:
        # Log the error
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8002)
