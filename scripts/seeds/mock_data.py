#!/usr/bin/env python3
import requests
import random
from typing import Dict, Any
from faker import Faker

USERS_COUNT = 1
PROJECTS_COUNT = 10  
DATA_ROOMS_COUNT = 15
API_BASE_URL = "http://localhost:8000"

fake = Faker()

class AuralisMockData:
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.created_users = []
        self.created_projects = []
        self.created_data_rooms = []
        
        self.business_contexts = [
            ("Merger & Acquisition", "Strategic M&A due diligence"),
            ("IPO Preparation", "Initial public offering readiness"),
            ("Debt Refinancing", "Corporate debt restructuring"),
            ("Private Equity", "PE investment documentation"),
            ("Real Estate Deal", "Commercial property development"),
            ("Asset Divestiture", "Non-core asset sale process"),
            ("Joint Venture", "Strategic partnership formation"),
            ("Regulatory Filing", "Compliance documentation"),
            ("Technology Transfer", "IP licensing agreement"),
            ("Contract Negotiation", "Major contract lifecycle")
        ]
    
    def api_call(self, method: str, endpoint: str, data: Dict[str, Any] | None = None) -> Dict[str, Any] | None:
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "POST":
                response = self.session.post(url, json=data)
            else:
                response = self.session.get(url)
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 204:
                return {"success": True}
            else:
                print(f"API error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("Cannot connect to API. Make sure server is running at http://localhost:8000")
            return None
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_user(self) -> Dict[str, Any]:
        return {
            "auth_provider_user_id": f"auth0|{fake.uuid4().replace('-', '')[:16]}"
        }
    
    def generate_project(self) -> Dict[str, Any]:
        business_type, description_base = random.choice(self.business_contexts)
        company = fake.company()
        quarter = random.choice(["Q1", "Q2", "Q3", "Q4"])
        year = random.choice([2024, 2025])
        
        return {
            "name": f"{company} - {business_type} ({quarter} {year})",
            "description": f"{description_base} for {company}. {fake.text(max_nb_chars=150)}"
        }
    
    def generate_data_room(self) -> Dict[str, Any]:
        company = fake.company()
        business_type = random.choice(self.business_contexts)[0]
        
        patterns = [
            f"Project {company} - {business_type}",
            f"{company} {business_type} Data Room",
            f"Confidential: {company} {business_type}",
            f"{business_type} - {company} Documentation"
        ]
        
        return {
            "name": random.choice(patterns),
            "source": random.choice(["original", "ansarada"])
        }
    
    def create_entities(self):
        print(f"Creating {USERS_COUNT} users...")
        for i in range(USERS_COUNT):
            user_data = self.generate_user()
            result = self.api_call("POST", "/users", user_data)
            if result:
                self.created_users.append(result)
                print(f"User {i+1}: {user_data['auth_provider_user_id'][:20]}...")
        
        print(f"Creating {PROJECTS_COUNT} projects...")
        for i in range(PROJECTS_COUNT):
            project_data = self.generate_project()
            result = self.api_call("POST", "/projects", project_data)
            if result:
                self.created_projects.append(result)
                name = project_data['name'][:50] + "..." if len(project_data['name']) > 50 else project_data['name']
                print(f"Project {i+1}: {name}")
        
        print(f"Creating {DATA_ROOMS_COUNT} data rooms...")
        for i in range(DATA_ROOMS_COUNT):
            room_data = self.generate_data_room()
            result = self.api_call("POST", "/data-rooms", room_data)
            if result:
                self.created_data_rooms.append(result)
                name = room_data['name'][:50] + "..." if len(room_data['name']) > 50 else room_data['name']
                print(f"Data room {i+1}: {name}")
    
    def link_entities(self):
        print("Creating relationships...")
        
        if not all([self.created_users, self.created_projects, self.created_data_rooms]):
            print("Missing entities, skipping relationships")
            return
        
        user_links = 0
        room_links = 0
        
        # Add the single user to all projects as admin
        user = self.created_users[0]
        for project in self.created_projects:
            endpoint = f"/projects/{project['id']}/users/{user['id']}"
            result = self.api_call("POST", endpoint, {"user_role": "admin"})
            if result:
                user_links += 1
        
        # Link data rooms to projects
        for project in self.created_projects:
            num_rooms = random.randint(1, min(3, len(self.created_data_rooms)))
            project_rooms = random.sample(self.created_data_rooms, num_rooms)
            
            for room in project_rooms:
                endpoint = f"/projects/{project['id']}/data-rooms/{room['id']}"
                result = self.api_call("POST", endpoint)
                if result:
                    room_links += 1
        
        print(f"Linked {user_links} user-project relationships")
        print(f"Linked {room_links} project-data room relationships")
    
    def run(self):
        print("Auralis Mock Data Generator")
        print("=" * 50)
        print(f"Target: {USERS_COUNT} users, {PROJECTS_COUNT} projects, {DATA_ROOMS_COUNT} data rooms")
        
        print("Testing API connection...")
        if not self.test_connection():
            print("Make sure your server is running: python -m uvicorn src.service_host.main:app --reload")
            return
        print("API is accessible")
        
        try:
            self.create_entities()
            self.link_entities()
            
            print("Generation completed successfully!")
            print(f"Created: {len(self.created_users)} users, {len(self.created_projects)} projects, {len(self.created_data_rooms)} data rooms")
            print(f"API docs: {self.base_url}/docs")
            
        except KeyboardInterrupt:
            print("Stopped by user")
        except Exception as e:
            print(f"Error: {e}")


def main():    
    generator = AuralisMockData()
    generator.run()


if __name__ == "__main__":
    main()