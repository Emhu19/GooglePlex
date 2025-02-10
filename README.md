# GooglePlex

**Googolplex** is a simplified search engine created as part of a scientific and technical project. This engine crawls web pages, indexes them, and enables fast searches using the **TF-IDF** algorithm to rank results by relevance. The project focuses primarily on technical aspects such as crawling, indexing, and searching.

## Table of Contents
1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Contributors](#contributors)
6. [License](#license)

## Features
- **Crawler**: Automatically explores web pages while respecting `robots.txt` rules.
- **Indexing**: Creates an inverted index to optimize searches.
- **Keyword Search**: Ranks results by relevance using the **TF-IDF** algorithm.
- **User-Friendly Interface**: An intuitive web interface for quick keyword searches.
- **Performance Optimization**: Handles high volumes of requests efficiently.

## Technologies Used
- **Language**: Python
- **Framework**: Django for the web interface.
- **Libraries**:
  - BeautifulSoup for web page scraping.
- **Database**: SQLite
- **Frontend**: HTML, CSS

## Installation

### Prerequisites
- Python 3.8+
- Git installed on your machine

### Steps

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Emhu_19/googolplex.git
   cd googolplex
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver

### Contributors

    Emhu_19 – Project creator
