import os
from pathlib import Path
import base64
from PIL import Image, ImageDraw, ImageFont
import io

def create_simple_png(text, size=(100, 100)):
    # Create a simple PNG with text
    # Create a new image with a white background
    image = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw text in the center
    draw.text((size[0]/2, size[1]/2), text, fill='black', anchor='mm')
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def setup_static_images():
    # Create directories
    base_dir = Path('app/static/images')
    for subdir in ['sports', 'leagues', 'teams']:
        (base_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    # List of all required images
    images = [
        # Sports
        ('sports/football.png', 'Football'),
        ('sports/basketball.png', 'Basketball'),
        ('sports/baseball.png', 'Baseball'),
        ('sports/hockey.png', 'Hockey'),
        
        # Leagues
        ('leagues/premier-league.png', 'Premier League'),
        ('leagues/la-liga.png', 'La Liga'),
        ('leagues/bundesliga.png', 'Bundesliga'),
        ('leagues/serie-a.png', 'Serie A'),
        ('leagues/nba.png', 'NBA'),
        ('leagues/euroleague.png', 'EuroLeague'),
        
        # Teams
        ('teams/manchester-united.png', 'Man United'),
        ('teams/liverpool.png', 'Liverpool'),
        ('teams/chelsea.png', 'Chelsea'),
        ('teams/arsenal.png', 'Arsenal'),
        ('teams/manchester-city.png', 'Man City'),
        ('teams/tottenham.png', 'Tottenham'),
        ('teams/real-madrid.png', 'Real Madrid'),
        ('teams/barcelona.png', 'Barcelona'),
        ('teams/atletico-madrid.png', 'Atletico'),
        ('teams/bayern-munich.png', 'Bayern'),
        ('teams/borussia-dortmund.png', 'Dortmund'),
        ('teams/rb-leipzig.png', 'Leipzig'),
        ('teams/juventus.png', 'Juventus'),
        ('teams/ac-milan.png', 'AC Milan'),
        ('teams/inter-milan.png', 'Inter'),
        ('teams/la-lakers.png', 'Lakers'),
        ('teams/golden-state-warriors.png', 'Warriors'),
        ('teams/chicago-bulls.png', 'Bulls'),
        ('teams/boston-celtics.png', 'Celtics'),
        ('teams/miami-heat.png', 'Heat'),
        ('teams/brooklyn-nets.png', 'Nets'),
        ('teams/real-madrid-basketball.png', 'RM Basketball'),
        ('teams/barcelona-basketball.png', 'Barca Basketball'),
        ('teams/cska-moscow.png', 'CSKA')
    ]
    
    # Create images
    for path, text in images:
        full_path = base_dir / path
        try:
            image_data = create_simple_png(text)
            with open(full_path, 'wb') as f:
                f.write(image_data)
            print(f'Created {path}')
        except Exception as e:
            print(f'Error creating {path}: {e}')

if __name__ == '__main__':
    setup_static_images()
