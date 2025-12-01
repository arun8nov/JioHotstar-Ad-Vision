# JioHotstar Ad Vision

**AI-powered Cricket Ad Recognition System**

## Overview

JioHotstar Ad Vision is a comprehensive application designed to track and analyze brand advertisements in cricket match videos. Leveraging AI and Computer Vision, it detects brand logos, tracks their screen time, and provides detailed analytics. The system also features a GenAI-powered chatbot for natural language database querying.

![image](Readme-image.png)

## Technical Implementation

The project is built using Python and relies on several key libraries and technologies. The core logic is encapsulated in `Base.py`, while the user interface is built with Streamlit in `app.py`.

### 1. Ad Tracking Engine (`Base.py`)

The `Tracking` class in `Base.py` handles the core computer vision tasks:

-   **Object Detection**: Uses **YOLO (You Only Look Once)**, specifically a custom-trained model (`Ad_track.pt`), to detect brand logos in video frames.
-   **Frame Processing**: The video is processed frame-by-frame. For each detection, the system records:
    -   **Confidence Score**: How certain the model is about the detection.
    -   **Bounding Box Coordinates**: The location of the logo on the screen.
    -   **Timestamp**: The exact time in the video where the logo appears.
-   **Brand Placement Logic**: The system automatically categorizes the placement of the ad based on the size (area) of the bounding box:
    -   **Jersey**: Area < 5000 pixels
    -   **Boundary**: 5000 < Area < 10000 pixels
    -   **Ground**: 10000 < Area < 50000 pixels
    -   **Overlay**: Area > 50000 pixels
-   **Data Storage**: Extracted data is saved to a CSV file and inserted into the MySQL database (`brands` table). Annotated frames are also saved to the disk.

### 2. Database Integration (`Base.py`)

The `Database_Intergration` class manages all interactions with the MySQL database:

-   **Connection**: Establishes connections using `mysql.connector` and `sqlalchemy`.
-   **Schema**:
    -   `matches`: Stores metadata about the match (ID, teams, location, winner, video path).
    -   `brands`: Stores detailed tracking data for every detected ad instance.
-   **Operations**: Handles inserting match data, querying tables for analytics, and resetting the database.

### 3. GenAI Chatbot (`Base.py`)

The `GenAi_Chat` class powers the "AI powered SQL Chatbot" feature:

-   **Natural Language to SQL**: Uses **LangChain** and **Google Gemini** (`gemini-2.5-flash`) to convert user questions (e.g., "Which brand appeared the most?") into executable SQL queries.
-   **Insight Generation**: After executing the generated SQL query, the results are fed back to the LLM to generate a natural language summary with key insights, trends, and recommendations.

### 4. Visualization (`Base.py`)

The `visual_charts` class generates interactive charts using **Plotly**:

-   **KPIs**: Total frames, total time, total brands, and total placements.
-   **Charts**:
    -   Brand Appearance Count (Bar Chart)
    -   Brand Position Distribution (Bar Chart)
    -   Brand Detection Trend over Frames (Area Chart)
    -   Brand Confidence Levels (Bar Chart)
    -   Brand Detection Time (Bar Chart)
    -   Heatmaps for Brand vs. Position

### 5. Frontend Interface (`app.py`)

The application is built using **Streamlit** and is organized into four main sections:

-   **Match Data Entry**: Allows users to input match details and upload a video. It triggers the ad tracking process upon submission.
-   **Add Tracking Visuals**: Displays the analytics dashboard for a specific match ID, utilizing the charts from `visual_charts`.
-   **Chat Interface**: Provides a chat interface for users to query the database using natural language.
-   **Admin Interface**: A password-protected section (`Admin@123`) to reset the database.

## Installation & Setup

### Prerequisites

-   **Python 3.8+**
-   **MySQL Server**: Ensure MySQL is installed and running.
-   **Google API Key**: Required for the GenAI features.

### Step-by-Step Guide

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/arun8nov/JioHotstar-Ad-Vision.git
    cd JioHotstar-Ad-Vision
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**
    Create a `.env` file in the root directory with the following credentials:
    ```env
    db_host="localhost"
    db_user="root"
    db_password="your_password"
    db_port="3306"
    db_name="jiohotstar_ads"
    api_key="your_google_api_key"
    ```

4.  **Database Setup**
    The application will automatically create the necessary database and tables if they don't exist when you run the "Reset Database" function in the Admin Interface or when inserting data.

5.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

## Usage

1.  **Upload a Match**: Go to **Match Data Entry**, fill in the details, and upload a video. Click "Insert Data & Add Tracking". Wait for the processing to complete.
2.  **View Analytics**: Go to **Add Tracking Visuals**, enter the Match ID, and click "Generate Visuals" to see the dashboard.
3.  **Ask Questions**: Go to **Chat Interface** and ask questions like "Show me the top 5 brands by duration".
4.  **Reset System**: Go to **Admin Interface**, enter the password (`Admin@123`), and click "Reset Database" to clear all data.

## Author

Arunprakash B

Mail: arunbabuprakash@gmail.com

Linkedin: https://www.linkedin.com/in/arun8nov/
