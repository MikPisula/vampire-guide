from typing import Union
from fastapi import FastAPI
from test_augment import test
from starlette.responses import RedirectResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/api/test_augment")
def test_augment(prefix_url = "/home/simon/Documents/vampire-guide/", start = "40.7466991,-73.9809522", end = "40.7478495,-73.9843726"):
    filename_html = "map.html"
    start_location = start.replace(' ', '').split(',')
    start_location = tuple(map(float, start_location))
    end_location =  end.replace(' ', '').split(',')
    end_location = tuple(map(float, end_location))
    
    print(f"{start_location=}, {end_location=}")
    
    try:
        test(
            html_output=filename_html,
            start_location=start_location,
            end_location=end_location
        )
    except Exception as e:
        print(f"Error: {e}")
        return {"Error": "this location is not supported, YET!"}
    map_file = FileResponse(filename_html, headers={"Cache-Control": "no-cache"})
    
    return map_file

app.mount('/', StaticFiles(directory="frontend/dist", html=True))
