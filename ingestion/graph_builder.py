import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TelegramChatFileLoader
from neo4j import GraphDatabase
import spacy

load_dotenv()

# Neo4j connection details
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_USERNAME = os. getenv("NEO4J_USERNAME")
NEO4J_URI = os.getenv("NEO4J_URI")

# Load the spaCy model for entity recognition
nlp = spacy.load("en_core_web_sm")

# Entity types to extract
ENTITY_TYPES = ["PERSON", "ORG", "GPE", "DATE", "TIME", "LOC", "PRODUCT", "EVENT", "MONEY"]
ENTITY_LABEL_MAP = {
    "PERSON": "Person",
    "ORG": "Organization",
    "GPE": "Location",
    "LOC": "Location",
    "DATE": "Date",
    "TIME": "Time",
    "PRODUCT": "Product",
    "EVENT": "Event",
    "MONEY": "Money"
}

def create_neo4j_session():
    driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))    
    return driver.session()

def load_telegram_docs():
    loader = TelegramChatFileLoader("./data/telegram_export/export.json")
    return loader.load()

def extract_entities(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        if ent.label_ in ENTITY_TYPES:
            entities.append((ent.text, ent.label_))
    return entities

def build_graph(docs):
    with create_neo4j_session() as session:
        for doc in docs:
            content = doc.page_content.strip()
            sender = doc.metadata.get("from", "Unknown")
            timestamp = doc.metadata.get("date", "Unknown")

            if not content:
                continue

            # Create sender node
            session.run("MERGE (p:Person {name: $sender})", sender=sender)

            # Create message node
            session.run("MERGE (m:Message {content: $content, timestamp: $timestamp})", 
                        content=content, timestamp=timestamp)
            
            # Create relationship between sender and message
            session.run("""
                MATCH (p:Person {name: $sender}), (m:Message {content: $content, timestamp: $timestamp})
                MERGE (p)-[:SENT]->(m)
            """, sender=sender, content=content, timestamp=timestamp)

            # Extract entities from the message content
            for entity_text, entity_type in extract_entities(content):
                label = ENTITY_LABEL_MAP.get(entity_type, entity_type.title())
                create_entity_query = f"MERGE (e:{label} {{name: $name}})"
                link_entity_query = f"""
                    MATCH (m:Message {{content: $content, timestamp: $timestamp}}), 
                          (e:{label} {{name: $name}})
                    MERGE (m)-[:MENTIONS]->(e)
                """
                session.run(create_entity_query, name=entity_text)
                session.run(link_entity_query, content=content, timestamp=timestamp, name=entity_text)

if __name__ == "__main__":
    docs = load_telegram_docs()
    build_graph(docs)
    print("Graph built successfully.")