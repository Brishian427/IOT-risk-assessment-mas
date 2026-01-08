"""
Populate RAG Database with Regulatory Documents

Run this script to initialize the RAG database with core regulatory content.
Users can extend this by adding their own documents.

Usage:
    python scripts/populate_rag_database.py
    python scripts/populate_rag_database.py --add-directory ./my_docs
    python scripts/populate_rag_database.py --skip-core  # Skip core documents

Created: 2025-01-XX
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.rag_database import get_rag_database


# Core regulatory documents
CORE_DOCUMENTS = [
    {
        "id": "psti_act_2024",
        "content": """
Product Security and Telecommunications Infrastructure Act 2022 (PSTI Act)
Effective: April 2024

KEY REQUIREMENTS FOR IoT DEVICES:

1. NO UNIVERSAL DEFAULT PASSWORDS
   - Each device must have unique password OR
   - User must set password before first use
   - Applies to all consumer connectable products

2. VULNERABILITY DISCLOSURE POLICY
   - Manufacturers must provide public contact point
   - Must acknowledge security reports within defined timeframe
   - Policy must be published and accessible

3. MINIMUM SECURITY UPDATE PERIOD
   - Must clearly state minimum period for security updates
   - Information must be available before purchase
   - Recommended minimum: 2 years (industry pushing for 5+)

4. STATEMENT OF COMPLIANCE
   - Manufacturers must provide compliance statement
   - Distributors must not sell non-compliant products

ENFORCEMENT:
- Regulatory enforcement body handles compliance
- Compliance notices requiring remedial action
- Recall notices for non-compliant products  
- Stop notices preventing further sales
- Fines up to £10 million or 4% of qualifying worldwide revenue

SCOPE:
- All consumer connectable products sold in UK
- Includes: smart speakers, cameras, doorbells, TVs, appliances
- Excludes: medical devices, smart meters, EV chargers (separate regulations)
        """,
        "metadata": {"type": "legislation", "jurisdiction": "UK", "year": 2024, "source": "UK Government"}
    },
    {
        "id": "etsi_en_303_645",
        "content": """
ETSI EN 303 645 - Cyber Security for Consumer Internet of Things
Version 2.1.1 (2020-06)

BASELINE SECURITY REQUIREMENTS (13 Provisions):

PROVISION 1: No universal default passwords
- Unique per device, or user-defined at setup
- No factory reset to universal default

PROVISION 2: Implement means to manage vulnerability reports
- Published vulnerability disclosure policy
- Act on vulnerabilities in timely manner

PROVISION 3: Keep software updated
- Securely updatable software
- Update mechanism cannot be disabled
- Users informed about security updates

PROVISION 4: Securely store sensitive security parameters
- Unique per device credentials stored securely
- Hard-coded credentials prohibited

PROVISION 5: Communicate securely
- Appropriate encryption for sensitive data
- Best practice cryptography

PROVISION 6: Minimize exposed attack surfaces
- Disable unused network interfaces
- Principle of least privilege
- Hardware attack surfaces considered

PROVISION 7: Ensure software integrity
- Verify software using secure boot
- Alert user/administrator if integrity failure

PROVISION 8: Ensure personal data is secure
- Sensitive data encrypted in transit and rest
- Cryptography reviewed regularly

PROVISION 9: Make systems resilient to outages
- Remain operating and locally functional
- Recover cleanly after power/network loss

PROVISION 10: Examine system telemetry data
- Anomaly detection where appropriate
- Security-relevant data should be examined

PROVISION 11: Make it easy to delete user data
- Clear function to delete personal data
- Clear instructions for data deletion

PROVISION 12: Make installation and maintenance easy
- Minimal steps with security guidance
- Best practice security enabled by default

PROVISION 13: Validate input data
- Data from networks and APIs validated
- Coding best practices followed

STATUS: Harmonised standard under EU Radio Equipment Directive
UK STATUS: Recognised standard post-Brexit, referenced in PSTI guidance
        """,
        "metadata": {"type": "standard", "jurisdiction": "EU/UK", "year": 2020, "source": "ETSI"}
    },
    {
        "id": "mirai_botnet_case_study",
        "content": """
CASE STUDY: Mirai Botnet Attack (2016)

OVERVIEW:
The Mirai botnet represents the most significant IoT-based cyber attack to date,
demonstrating the systemic risks of insecure consumer IoT devices.

ATTACK MECHANISM:
- Malware scanned internet for IoT devices with open Telnet/SSH
- Attempted login using list of 62 common default credentials
- Successfully compromised devices joined botnet
- Infected devices scanned for additional targets (exponential growth)

SCALE:
- Peak: 600,000+ compromised devices
- Device types: IP cameras, DVRs, routers, smart home devices
- Geographic spread: Global, concentrated in Asia and South America

IMPACT - October 2016 Dyn DNS Attack:
- Targeted Dyn, major DNS provider
- Traffic reached 1.2 Tbps (largest DDoS at time)
- Services affected: Twitter, Netflix, Reddit, GitHub, PayPal, Spotify
- Outage duration: Multiple hours across three attack waves
- Estimated economic impact: $110 million+

ROOT CAUSES:
1. Universal default passwords (admin/admin, root/root, etc.)
2. Exposed network services (Telnet on port 23)
3. No firmware update capability on many devices
4. Lack of network segmentation
5. No anomaly detection or rate limiting

REGULATORY RESPONSE:
- Directly influenced UK PSTI Act default password ban
- Cited in ETSI EN 303 645 development rationale
- Led to California SB-327 (2018) - first US IoT security law
- Prompted NIST IoT security guidelines

LESSONS FOR RISK ASSESSMENT:
- Default credentials remain primary attack vector
- Consumer IoT devices can cause systemic harm
- Volume of insecure devices creates collective risk
- Lifecycle management (updates) critical
- Supply chain security essential

CURRENT STATUS:
- Mirai variants continue to evolve
- Mozi, BotenaGo, and other IoT botnets active
- Default credential exploitation still primary vector
        """,
        "metadata": {"type": "case_study", "year": 2016, "source": "Security Research"}
    },
    {
        "id": "uk_gdpr_iot_implications",
        "content": """
UK GDPR and Data Protection Act 2018 - IoT Implications

LAWFUL BASIS FOR IoT DATA PROCESSING:
Under UK GDPR, IoT manufacturers and operators must establish lawful basis:
- Consent: User actively agrees to data collection
- Contract: Processing necessary for service delivery
- Legitimate interests: Balanced against user rights

IoT-SPECIFIC CHALLENGES:

1. CONTINUOUS DATA COLLECTION
- Smart devices collect data 24/7
- Often exceeds user expectations
- Voice assistants record ambient audio
- Location tracking continuous

2. CONSENT VALIDITY
- Terms buried in lengthy agreements
- Users may not understand scope
- Consent should be specific, informed, unambiguous
- Children's data requires parental consent

3. DATA MINIMIZATION PRINCIPLE
- Collect only what's necessary
- IoT often collects more than needed
- Purpose limitation applies

4. RIGHTS OF DATA SUBJECTS
- Right to access: Users can request their data
- Right to erasure: "Right to be forgotten"
- Right to portability: Data in machine-readable format
- Right to object: Stop processing for certain purposes

5. PRIVACY BY DESIGN (Article 25)
- Data protection built into products
- Default settings should be privacy-protective
- Not retrofitted after development

6. HOUSEHOLD DATA COMPLEXITY
- Multiple people affected by single device
- Bystander data (visitors, neighbors)
- Fairhurst v Woodard (2021): Ring doorbell capturing beyond property

IoT DATA BREACH REQUIREMENTS:
- Report to ICO within 72 hours if risk to individuals
- Notify affected individuals if high risk
- Document all breaches regardless of reporting

PENALTIES:
- Up to £17.5 million or 4% of annual global turnover
- ICO enforcement actions increasing
        """,
        "metadata": {"type": "legislation", "jurisdiction": "UK", "year": 2018, "source": "ICO Guidance"}
    },
    {
        "id": "weee_iot_disposal",
        "content": """
Waste Electrical and Electronic Equipment (WEEE) Regulations - IoT Context

UK WEEE REGULATIONS 2013 (as amended)

PRODUCER RESPONSIBILITIES:
- Register with approved compliance scheme
- Report quantities placed on UK market
- Finance collection, treatment, recovery, disposal
- Provide disposal information to consumers

IoT-SPECIFIC DISPOSAL CHALLENGES:

1. LITHIUM BATTERY HAZARDS
- Most IoT devices contain lithium batteries
- Fire risk if damaged or improperly disposed
- Thermal runaway can occur in waste facilities
- 700+ fires in UK waste facilities (2023) linked to batteries
- Separate collection mandatory

2. DATA PERSISTENCE
- Personal data remains on device storage
- Factory reset may not fully erase
- Cloud account linkage may persist
- GDPR obligations extend to disposal phase

3. RARE EARTH MATERIALS
- IoT devices contain critical materials
- Recovery rates currently low
- Indium, gallium in displays
- Neodymium in speakers/motors

4. E-WASTE GROWTH
- IoT driving WEEE volume increase
- Short product lifecycles (3-5 years typical)
- Collection infrastructure struggling
- UK WEEE collection rate: ~40% (target: 65%)

LIFECYCLE RISK IMPLICATIONS:
- Undisposed devices may leak data
- Improper disposal creates fire hazards
- Rare material loss affects supply chain
- Regulatory compliance extends to end-of-life

CONSUMER GUIDANCE (Required):
- Crossed-out wheelie bin symbol on products
- Take-back schemes at retailers
- Local authority collection points
- Producer-funded postal return schemes
        """,
        "metadata": {"type": "legislation", "jurisdiction": "UK", "year": 2024, "source": "Environment Agency"}
    },
    {
        "id": "iot_market_statistics_2024",
        "content": """
IoT Market Statistics and Projections (2024-2030)

UK MARKET DATA:
- UK IoT market value: £16.5 billion (2022)
- Average connected devices per UK household: 10.3 (Aviva, 2020)
- Forecast growth: 14% annually

GLOBAL MARKET:
- Installed IoT devices: 15.14 billion (2024)
- Projected 2030: 29.4 billion devices
- Consumer IoT: ~60% of total market
- Industrial IoT: ~40% of total market

DEVICE CATEGORIES (UK Consumer):
- Smart speakers: 39% of households
- Smart TVs: 65% of households  
- Smart security: 18% of households
- Smart thermostats: 12% of households
- Smart appliances: 8% of households

SECURITY INCIDENT DATA:
- 112 million IoT attacks globally (2022)
- Average time to compromise unsecured IoT: 5 minutes
- 57% of IoT devices vulnerable to medium/high severity attacks
- Default credential exploitation: #1 attack vector

REGULATORY IMPACT PROJECTIONS:
- PSTI Act compliance cost: £2-5 per device
- Expected non-compliance at launch: 30-40% of market
- Enforcement actions projected: 100+ in first year

MARKET RISK FACTORS:
- Supply chain concentration (TSMC: 90% of advanced chips)
- Cloud service dependency (AWS/Azure/Google: 65% of IoT cloud)
- Geopolitical risks affecting component supply
- Skills shortage in IoT security
        """,
        "metadata": {"type": "market_data", "year": 2024, "source": "Industry Reports"}
    }
]


def populate_core_documents():
    """Populate database with core regulatory documents"""
    db = get_rag_database()
    
    if db is None:
        print("❌ RAG database not available. Install ChromaDB: pip install chromadb sentence-transformers")
        return
    
    print("\n📚 Populating RAG Database with Core Documents...")
    print("="*50)
    
    for doc in CORE_DOCUMENTS:
        db.add_document(
            content=doc["content"],
            doc_id=doc["id"],
            metadata=doc["metadata"]
        )
        print(f"  ✅ Added: {doc['id']}")
    
    print("="*50)
    stats = db.get_stats()
    print(f"\n📊 Database Statistics:")
    print(f"   Documents: {stats['document_count']}")
    print(f"   Location: {stats['persist_directory']}")


def add_custom_directory(directory: str):
    """Add documents from a custom directory"""
    db = get_rag_database()
    
    if db is None:
        print("❌ RAG database not available. Install ChromaDB: pip install chromadb sentence-transformers")
        return
    
    print(f"\n📂 Adding documents from: {directory}")
    count = db.add_documents_from_directory(directory)
    print(f"   Added {count} documents")


def main():
    parser = argparse.ArgumentParser(description="Populate RAG Database")
    parser.add_argument("--add-directory", type=str, help="Add documents from directory")
    parser.add_argument("--skip-core", action="store_true", help="Skip core documents")
    
    args = parser.parse_args()
    
    if not args.skip_core:
        populate_core_documents()
    
    if args.add_directory:
        add_custom_directory(args.add_directory)
    
    # Test query
    db = get_rag_database()
    if db:
        print("\n🔍 Test Query: 'default password requirements'")
        results = db.query("default password requirements", n_results=2)
        for r in results:
            print(f"   - {r['id']} (distance: {r.get('distance', 'N/A')})")


if __name__ == "__main__":
    main()

