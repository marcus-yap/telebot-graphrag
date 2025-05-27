from neo4j import GraphDatabase
import re
from datetime import datetime

class GraphRetriever:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def retrieve_by_entity(self, entity_name):
        query = """
        MATCH (m:Message)-[:MENTIONS]->(e {name: $entity})
        RETURN m.content AS content, m.timestamp AS timestamp
        ORDER BY m.timestamp DESC
        LIMIT 20
        """
        with self.driver.session() as session:
            result = session.run(query, entity=entity_name)
            return [{"content": record["content"], "timestamp": record["timestamp"]} for record in result]

    def retrieve_by_type(self, entity_type):
        allowed_labels = ["Person", "Organization", "Location", "Date", "Time", "Product", "Event", "Money"]
        if entity_type not in allowed_labels:
            return []

        query = f"""
        MATCH (m:Message)-[:MENTIONS]->(e:{entity_type})
        RETURN m.content AS content, m.timestamp AS timestamp
        ORDER BY m.timestamp DESC
        LIMIT 20
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [{"content": record["content"], "timestamp": record["timestamp"]} for record in result]

    def retrieve_by_date(self, start_date, end_date):
        query = """
        MATCH (m:Message)
        WHERE m.timestamp >= $start_date AND m.timestamp <= $end_date
        RETURN m.content AS content, m.timestamp AS timestamp
        ORDER BY m.timestamp DESC
        LIMIT 20
        """
        with self.driver.session() as session:
            result = session.run(query, start_date=start_date, end_date=end_date)
            return [{"content": record["content"], "timestamp": record["timestamp"]} for record in result]

    def retrieve_by_sender(self, sender_name):
        query = """
        MATCH (p:Person {name: $sender})-[:SENT]->(m:Message)
        RETURN m.content AS content, m.timestamp AS timestamp
        ORDER BY m.timestamp DESC
        LIMIT 20
        """
        with self.driver.session() as session:
            result = session.run(query, sender=sender_name)
            return [{"content": record["content"], "timestamp": record["timestamp"]} for record in result]

    def retrieve(self, query: str):
        query = query.strip()

        # Handle date range queries: "2023-01-01 to 2023-01-31"
        match = re.search(r"(\d{4}-\d{2}-\d{2})\s*(to|-)\s*(\d{4}-\d{2}-\d{2})", query)
        if match:
            start_date = match.group(1)
            end_date = match.group(3)
            return self.retrieve_by_date(start_date, end_date)

        # Handle sender query: "from Alice" or "by Alice"
        if match := re.search(r"(from|by)\s+(.+)", query, re.IGNORECASE):
            sender_name = match.group(2)
            return self.retrieve_by_sender(sender_name)

        # Handle type queries: "type:Person"
        if match := re.search(r"type:(\w+)", query):
            entity_type = match.group(1).capitalize()
            return self.retrieve_by_type(entity_type)

        # Fallback to entity-based retrieval
        return self.retrieve_by_entity(query)