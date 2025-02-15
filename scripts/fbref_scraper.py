import requests
from bs4 import BeautifulSoup
import csv
import time
from random import uniform
import os

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': 'https://www.google.com'
    }

def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def save_html(html_content, page_number, directory):
    ensure_directory(directory)
    filename = f"{directory}/page_{page_number}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Saved HTML for page {page_number}")

def scrape_fbref(base_url, min_players=1000):
    players_data = []
    player_id = 1
    page_number = 1
    session = requests.Session()
    html_dir = "fbref_html"
    
    try:
        print("Starting initial page scrape...")
        response = session.get(base_url, headers=get_headers())
        response.raise_for_status()
        
        save_html(response.text, page_number, html_dir)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        while len(players_data) < min_players:
            player_table = soup.find('table', id='stats_standard')
            if not player_table:
                print("Table not found")
                break
                
            player_rows = player_table.find('tbody').find_all('tr')
            
            for row in player_rows:
                if 'thead' in row.get('class', []):
                    continue
                    
                player = {}
                player['ID'] = f'f{player_id}'
                
                name_element = row.find('td', {'data-stat': 'player'})
                player['name'] = name_element.text.strip() if name_element else ''
                
                position_element = row.find('td', {'data-stat': 'position'})
                player['position'] = position_element.text.strip() if position_element else ''
                
                age_element = row.find('td', {'data-stat': 'age'})
                if age_element and age_element.text.strip():
                    age_full = age_element.text.strip()
                    player['age'] = age_full.split('-')[0] if '-' in age_full else age_full
                else:
                    player['age'] = ''
                
                nation_element = row.find('td', {'data-stat': 'nationality'})
                player['nationality'] = nation_element.text.strip() if nation_element else ''
                
                club_element = row.find('td', {'data-stat': 'team'})
                player['current_club'] = club_element.text.strip() if club_element else ''
                
                matches_element = row.find('td', {'data-stat': 'games'})
                player['matches_played'] = matches_element.text.strip() if matches_element else ''
                
                players_data.append(player)
                player_id += 1
                
                print(f"Scraped {len(players_data)} players...")
            
            next_page = soup.find('a', string='Next page')
            if not next_page:
                print("No more pages available")
                break
                
            next_url = 'https://fbref.com' + next_page['href']
            print(f"Moving to next page: {next_url}")
            
            time.sleep(uniform(2, 3))
            
            page_number += 1
            response = session.get(next_url, headers=get_headers())
            response.raise_for_status()
            
            save_html(response.text, page_number, html_dir)
            soup = BeautifulSoup(response.text, 'html.parser')
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return players_data
    
    return players_data

def save_to_csv(players_data, filename):
    if not players_data:
        print("No data to save")
        return
        
    headers = ['ID', 'name', 'position', 'age', 'nationality', 'current_club', 'matches_played']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(players_data)
        print(f"Saved {len(players_data)} players to {filename}")

def main():
    base_url = "https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats"
    players = scrape_fbref(base_url)
    
    if players:
        save_to_csv(players, 'tableB.csv')
        print(f"Successfully scraped {len(players)} players")

if __name__ == "__main__":
    main()