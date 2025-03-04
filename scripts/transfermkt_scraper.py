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

def scrape_transfermarkt(base_url, min_players=1000):
    players_data = []
    player_id = 1
    page = 1
    html_dir = "transfermarkt_html"
    
    while len(players_data) < min_players:
        try:
            url = f"{base_url}?page={page}"
            print(f"Scraping page {page}...")
            
            response = requests.get(url, headers=get_headers())
            response.raise_for_status()
            
            save_html(response.text, page, html_dir)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            player_table = soup.find('table', class_='items')
            if not player_table:
                print(f"No more tables found on page {page}")
                break
                
            player_rows = player_table.find_all('tr', class_=['odd', 'even'])
            if not player_rows:
                print(f"No more players found on page {page}")
                break
            
            for row in player_rows:
                player = {}
                player['ID'] = f't{player_id}'
                
                name_element = row.find('td', class_='hauptlink')
                if name_element and name_element.find('a'):
                    player['name'] = name_element.find('a').text.strip()
                else:
                    player['name'] = ''
                inline_table = row.find('table', class_='inline-table')
                if inline_table:
                    position_rows = inline_table.find_all('tr')
                    if len(position_rows) > 1:
                        position_cell = position_rows[1].find('td')
                        if position_cell:
                            player['position'] = position_cell.text.strip()
                        else:
                            player['position'] = ''
                    else:
                        player['position'] = ''
                else:
                    player['position'] = ''
                
                age_cells = row.find_all('td', class_='zentriert')
                if len(age_cells) >= 2:
                    player['age'] = age_cells[1].text.strip()
                else:
                    player['age'] = ''
                
                nationality_element = row.find('img', class_='flaggenrahmen')
                player['nationality'] = nationality_element['title'] if nationality_element and 'title' in nationality_element.attrs else ''
                
                value_element = row.find('td', class_='rechts hauptlink')
                player['market_value'] = value_element.text.strip() if value_element else ''
                
                players_data.append(player)
                player_id += 1
                
                print(f"Scraped {len(players_data)} players...")
            
            page += 1
            time.sleep(uniform(2, 3))
            
        except Exception as e:
            print(f"An error occurred on page {page}: {str(e)}")
            time.sleep(5)
            continue
            
        if page > 100:
            print("Reached maximum page limit")
            break
    
    return players_data

def save_to_csv(players_data, filename):
    if not players_data:
        print("No data to save")
        return
        
    headers = ['ID', 'name', 'position', 'age', 'nationality', 'market_value']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(players_data)
        print(f"Saved {len(players_data)} players to {filename}")

def main():
    base_url = "https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop"
    players = scrape_transfermarkt(base_url)
    
    if players:
        save_to_csv(players, 'tableA.csv')
        print(f"Successfully scraped {len(players)} players")

if __name__ == "__main__":
    main()
