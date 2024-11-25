import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.sources = {
            'espn': 'https://www.espn.com/{sport}',
            'sports_illustrated': 'https://www.si.com/{sport}',
            'bbc_sport': 'https://www.bbc.com/sport/{sport}'
        }
        
    def get_news(self, sport='all', limit=10):
        """Get sports news from various sources"""
        news_items = []
        try:
            if sport == 'football':
                news_items.extend(self._scrape_espn('soccer'))
                news_items.extend(self._scrape_bbc('football'))
            elif sport == 'basketball':
                news_items.extend(self._scrape_espn('nba'))
                news_items.extend(self._scrape_espn('ncb'))
            else:
                # Get news from all sports
                sports = ['soccer', 'nba', 'nfl', 'mlb']
                for s in sports:
                    news_items.extend(self._scrape_espn(s))
            
            # Sort by date and limit
            news_items.sort(key=lambda x: x['date'], reverse=True)
            return news_items[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []
    
    def _scrape_espn(self, sport):
        """Scrape news from ESPN"""
        news_items = []
        try:
            url = self.sources['espn'].format(sport=sport)
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = soup.find_all('article', class_='news-feed-item')
            for article in articles:
                try:
                    title = article.find('h1').text.strip()
                    link = article.find('a')['href']
                    if not link.startswith('http'):
                        link = f"https://www.espn.com{link}"
                    
                    date_str = article.find('span', class_='timestamp').text.strip()
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    news_items.append({
                        'title': title,
                        'link': link,
                        'source': 'ESPN',
                        'sport': sport,
                        'date': date
                    })
                except Exception as e:
                    logger.error(f"Error parsing ESPN article: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping ESPN: {str(e)}")
            
        return news_items
    
    def _scrape_bbc(self, sport):
        """Scrape news from BBC Sport"""
        news_items = []
        try:
            url = self.sources['bbc_sport'].format(sport=sport)
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = soup.find_all('div', class_='gs-c-promo')
            for article in articles:
                try:
                    title = article.find('h3').text.strip()
                    link = article.find('a')['href']
                    if not link.startswith('http'):
                        link = f"https://www.bbc.com{link}"
                    
                    date = datetime.now()  # BBC doesn't show article dates on listing
                    
                    news_items.append({
                        'title': title,
                        'link': link,
                        'source': 'BBC Sport',
                        'sport': sport,
                        'date': date
                    })
                except Exception as e:
                    logger.error(f"Error parsing BBC article: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping BBC: {str(e)}")
            
        return news_items
