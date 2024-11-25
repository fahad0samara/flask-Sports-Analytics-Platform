from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class PredictionForm(FlaskForm):
    predicted_winner = SelectField('Predict Winner', 
                                 coerce=int,
                                 validators=[DataRequired()])
    confidence = FloatField('Confidence Level (0-100)',
                          validators=[
                              DataRequired(),
                              NumberRange(min=0, max=100, 
                                        message='Confidence must be between 0 and 100')
                          ])
    submit = SubmitField('Submit Prediction')
