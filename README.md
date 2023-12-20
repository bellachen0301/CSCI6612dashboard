# Time Series Analysis Web Application with ARIMA and Dash

This web application is designed to guide users through the process of analyzing time series data and fitting an ARIMA model for making predictions. Built with Plotly Dash and Python, it offers an interactive environment to visualize data trends and forecast future values.

## Getting Started

### Prerequisites

Before running the application, ensure you have Python installed on your local machine. The application is developed and tested with Python 3.10.12

### Installation

#### Clone the Repository

Begin by cloning the repository to your local machine using Git.

```sh
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

#### Create a Virtual Environment
It is recommended to create a virtual environment to manage the dependencies for the project.
<br>Start with creating the virtual environment.
```sh
python -m venv venv
```

On Windows:
```sh
.\venv\Scripts\activate
```

On Unix or MacOS:
```sh
source venv/bin/activate
```
#### Install Dependencies
Install all the required libraries using pip by referencing the requirements.txt file.

```sh
pip install -r requirements.txt
```

#### Run the Application
Once the dependencies are installed, you can run the application using the following command:


```sh
python app.py
```

The application will start and be available at http://127.0.0.1:8050/ in your web browser.

## Usage

The application provides a step-by-step approach to time series analysis:

Upload your data and visualize time series trends.
Decompose the series to identify residuals.
Select parameters for the ARIMA model and fit it to your data.

## Reference

This Project is refered to the accompanying article on Medium. 
Supporting article: [available on Medium](https://medium.com/towards-data-science/time-series-data-analysis-with-sarima-and-dash-f4199c3fc092)
This article provides an overview of the application's functionality and underlying concepts.

