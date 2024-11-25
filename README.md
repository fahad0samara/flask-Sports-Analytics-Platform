# Sports Analytics Platform

A comprehensive Flask-based web application for sports analytics and predictions, featuring machine learning integration, multi-sport support, and social features.

## Features

- User Authentication System (Admin, Analyst, User roles)
- Multi-Sport Support (Football, Basketball, Baseball)
- Machine Learning Integration
  - Win probability predictions
  - Player performance forecasting
  - Team statistics analysis
  - Historical trend analysis
- Advanced Data Visualization
- Social Features (Forums, Predictions sharing)
- Real-time Updates
- Mobile Responsive Design

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sports_analytics
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///sports_analytics.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
WEATHER_API_KEY=your-weather-api-key
SPORTS_API_KEY=your-sports-api-key
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
flask run
```

## Project Structure

```
sports_analytics/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── main/
│   ├── api/
│   ├── predictions/
│   ├── admin/
│   └── templates/
├── migrations/
├── tests/
├── venv/
├── config.py
├── requirements.txt
└── run.py
```

## API Documentation

The application provides several REST API endpoints:

- `/api/v1/matches`: Get match information
- `/api/v1/predictions`: Get/create predictions
- `/api/v1/teams`: Team information
- `/api/v1/players`: Player statistics
- `/api/v1/users`: User management (admin only)

## Machine Learning Models

The application uses several machine learning models for predictions:

- Win Probability: Gradient Boosting
- Player Performance: LSTM Neural Networks
- Team Analysis: Random Forest
- Historical Trends: Time Series Analysis

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
