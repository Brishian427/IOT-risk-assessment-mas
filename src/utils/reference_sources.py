"""
Reference Sources for Multi-Agent Risk Assessment

HYBRID APPROACH:
This module provides reference sources using a hybrid approach:
1. RAG database (dynamic, query-specific) - if available
2. Hardcoded baseline sources (always included as fallback)

The get_reference_sources() function now delegates to rag_database.py
which combines RAG retrieval with this hardcoded baseline.

Created: 2025-12-09
Updated: 2025-01-XX (Hybrid RAG + hardcode support)
"""

# Reference sources in structured format (BASELINE - always included)
REFERENCE_SOURCES = """
=== REFERENCE SOURCES FOR RISK ASSESSMENT ===

These sources provide authoritative context, statistics, and industry insights that should be referenced when evaluating IoT risk scenarios.

1. MARKET POTENTIAL & ECONOMIC IMPACT
   - By 2030, the IoT suppliers' market is expected to reach approximately $500 billion in a baseline scenario. If cybersecurity concerns are managed, the total addressable market (TAM) could reach between $625 billion and $750 billion.
   - The full potential value of the IoT by 2030, taking into account broad societal benefit, utility, and productivity, is estimated to be between $5.5 trillion and $12.6 trillion.

2. BUYER BEHAVIOR & ADOPTION DRIVERS
   - Approximately 40% of survey respondents indicated they would increase their IoT budget and deployment by 25% or more if cybersecurity concerns were resolved.
   - There is a gap in perception regarding digital trust: 61% of IoT buyers rank digital trust as a critical purchase element, whereas only 31% of IoT providers rank it as critical in system design.
   - 81% of IoT providers blame siloed decision-making between IoT and cybersecurity groups on the buyer side for adoption delays. However, only 42% of buyers agree with this assessment.

3. CYBERSECURITY FRAMEWORK
   - IoT security requires expanding the traditional CIA (Confidentiality, Integrity, Availability) framework. It must include six outcomes:
     * Data privacy and Access (Confidentiality)
     * Reliability and Compliance (Integrity)
     * Uptime and Resilience (Availability)

4. INDUSTRY VERTICAL FOCUS AREAS
   - Automotive IoT: Projected to reach $100 billion by 2030. Primary cybersecurity focus is 'Availability' (resilience and uptime) to prevent collisions and safety hazards in autonomous and connected vehicles.
   - Healthcare IoT: Projected to reach $70 billion by 2030. Primary cybersecurity focus is 'Confidentiality' (patient privacy) and 'Availability' (data-driven care decisions).
   - Smart Cities IoT: Projected to reach $30 billion by 2030. Primary cybersecurity focus is 'Integrity' (data reliability) due to cross-cutting nature and multiple stakeholders.

5. TECHNICAL CONVERGENCE & INTEGRATION
   - Convergence of IoT and cybersecurity can occur at three levels:
     1. Architectural (secured code in backbone software)
     2. Parallel-design (partnering throughout the design process)
     3. Software add-on (installing additional solutions to secure applications)

6. ADOPTION BARRIERS & PAIN POINTS
   - Key factors inhibiting a seamless IoT experience include: Confidentiality, Connectivity performance, Cybersecurity, Installation complexities, Interoperability, Privacy, and Technology performance.

7. LABOR MARKET & TALENT CHALLENGES
   - A major obstacle to convergence is the global cybersecurity talent shortage, specifically the lack of talent possessing expertise in both IoT architecture and enterprise cybersecurity.

8. VULNERABILITY LAYERS
   - According to the McKinsey B2B IoT Survey, the 'IoT application software' and 'human-machine interfaces' are considered the most vulnerable layers of the IoT stack.

9. MARKET MATURITY & CONVERGENCE STATUS
   - While 80% of providers embed some form of security, only 50% are building holistic solutions for both cybersecurity and IoT.
   - 60% of providers are choosing to partner with other companies rather than building capabilities in-house.

10. REAL-WORLD SECURITY INCIDENTS & CASE STUDIES
   These documented incidents demonstrate actual risk manifestations and should be referenced when evaluating similar scenarios:
   
   a) Infrastructure Attacks & Physical Safety (Usage Phase):
      - Finland HVAC DDoS Attack (2016): A DDoS attack caused central heating systems to enter a reboot loop and shut down for over a week during sub-zero temperatures. This highlights the critical risk to 'Availability' and physical safety (hypothermia). Source: The Hacker News (2016)
      - UK Smart Meter GCHQ Intervention: GCHQ raised concerns that universal SMETS 2 meters could be hacked to inflate bills, compromise data, or cause a power surge to the National Grid. Metadata analysis enables burglary targeting. Source: The Telegraph / Computer Weekly
   
   b) Remote Direct Control & Harassment (Usage Phase):
      - Ring Camera 'Santa Claus' Hack (2019): A hacker harassed an 8-year-old via a compromised Ring camera's 2-way audio, proving the severe psychological and privacy impact of remote control vulnerabilities. Breach was due to weak user credentials, not system breach. Source: CNN (2019)
      - South Korea IP Camera Mass Hack (2024): Four individuals hacked 120,000 private IP cameras in homes and businesses, specifically targeting intimate areas to sell sexually exploitative footage. Breach exploited simple passwords. Source: The Washington Post (2024)
   
   c) Mass Data Breaches & Systemic Vulnerabilities (Usage Phase):
      - Mirai Botnet (2016): Malware scanned the internet for devices using default passwords (61 combinations), enslaving 600,000 devices for massive DDoS attacks. Proves reliance on user vigilance is a systemic failure. Source: CSO Online / Imperva Incapsula
      - Mars Hydro Database Leak: Unprotected database exposed 2.7 billion records, including plaintext Wi-Fi passwords and API credentials. This data enables 'nearest neighbor' and credential stuffing attacks. Source: Infosecurity Magazine (2025)
      - iRobot Roomba Image Leak: Development Roombas captured images of users in private situations (e.g., on the toilet) which were sent to third-party data labelers (Scale AI) and subsequently leaked online. This highlights the risk of 'Human-in-the-Loop' data training pipelines for AI-enabled appliances. Source: MIT Technology Review
   
   d) User Awareness & Legal Compliance (Usage Phase):
      - Fairhurst v Woodard (Ring Doorbell Lawsuit): UK court ruled homeowner violated privacy laws by recording audio outside property boundaries with a smart doorbell. Highlights user ignorance of legal obligations (legal liability risk). Source: The Scotsman (2021)
   
   e) Protocol Weaknesses (Usage Phase):
      - BlueBorne Bluetooth Exploit (2017): Exploitation of 8 sophisticated Bluetooth flaws allows attackers to take control of affected devices (20 million Amazon Echo and Google Home devices vulnerable) without user interaction, highlighting the risk of fundamental communication protocols. Source: The Hacker News (2017)
   
   f) Cloud Dependence & Trust (Usage Phase):
      - Ring Backend Glitch (May 2025): A backend update bug caused Ring apps to inaccurately display 'unauthorized logins' from a specific date. This non-malicious error severely eroded digital trust, highlighting cloud resilience and display complexity issues. Source: Snopes (2025)
      - UK Smart Meter Rollout Delays: UK Smart Meter rollout faced delays and fines due to provider mismanagement (E.on, British Gas). Ring doorbell users reported widespread functional outages due to backend glitches.
   
   Key Lessons from Case Studies:
   - Default passwords and weak authentication are systemic vulnerabilities (Mirai, Ring, South Korea cameras)
   - Infrastructure attacks can cause physical harm (Finland HVAC, UK smart meters)
   - Privacy violations have severe psychological and safety impacts (Ring harassment, South Korea cameras, Roomba)
   - Data breaches enable secondary attacks (Mars Hydro Wi-Fi passwords, smart meter metadata)
   - User awareness and 2FA adoption are critical failure points
   - Third-party data processing introduces additional privacy risks (Roomba/Scale AI)
   - Legal liability extends to users who violate privacy laws (Fairhurst v Woodard)
   - Protocol-level vulnerabilities affect millions of devices simultaneously (BlueBorne)
   - Cloud service reliability directly impacts device functionality and user trust

11. FIRMWARE & MANUFACTURING SECURITY (Manufacturing Phase)
   - Firmware Vulnerability Statistics: 83% of firms polled had at least one firmware attack in the last two years (Microsoft survey). 70% of businesses without a firmware updating plan will experience a firmware-related breach by the end of 2022 (Gartner). Source: Bhardwaj et al. (2023) / Gartner
   - Firmware Analysis Method: Proposed unique twelve-step process to perform forensic analysis and security assessment of Smart IoT Camera firmware. Firmware is the most neglected area of device security. Source: Bhardwaj et al. (2023)
   - Hardcoded Secrets in D-Link Firmware: Forensic analysis of D-Link DCS-5020L camera firmware found hardcoded usernames, passwords, SSL keys, IP Addresses, and URLs residing in the extracted filesystem. This is a critical information disclosure risk. Source: Bhardwaj et al. (2023)
   - Gateway Architecture for Security: The Gateway architecture is preferred for Smart Homes. It uses a resource-rich central processor to offload computation, centralize authentication, act as a firewall, and manage automatic updates for constrained IoT devices. Source: Lin et al. (2016)

12. END-OF-LIFE (EOL) RISKS
   - EOL Fire Risk & Awareness Gap: 45% of householders are unaware of fire risks from lithium-ion batteries in old devices. Hoarding creates 'ignition risk' in drawers/cupboards due to battery degradation or short circuits. Source: Material Focus
   - Toxic Leaching Mechanism: Improper landfill disposal leads to leaching of toxic metals (Indium, Gallium) and Brominated Flame Retardants (BFRs) from plastics into soil and water, affecting human reproductive systems and crops. Source: DesignLifecycle / Environmental Impact Studies
   - Xiaomi Mi Robot Permanent Data: Xiaomi Mi Robot collects Lidar sensor maps and Wi-Fi passwords daily. This data remains in the system forever, even after a factory reset, posing a severe data leakage risk if the device is resold. Source: Kaspersky (2018)

13. LACK OF CONTINUOUS UPDATES (Usage Phase)
   - Lack of Continuous Security Support: Manufacturers stop providing security updates shortly after sale, leaving known vulnerabilities unfixed indefinitely (e.g., Amazon Echo 2nd Gen and Google Nest stopped receiving security patches for 2-3 years). Source: Which? (UK consumer organization) / Cybersecurity Insiders (2024)

=== END OF REFERENCE SOURCES ===
"""


def get_reference_sources(risk_topic: str = "", use_rag: bool = True) -> str:
    """
    Get formatted reference sources for use in prompts.
    
    HYBRID APPROACH:
    - Delegates to rag_database.get_reference_sources() which combines:
      1. RAG database (dynamic, query-specific) - if available
      2. Hardcoded baseline (this module) - always included
    
    Args:
        risk_topic: Optional topic to focus RAG retrieval
        use_rag: Whether to attempt RAG retrieval (default: True)
    
    Returns:
        Formatted context string combining RAG + hardcoded baseline
    """
    # Import here to avoid circular imports
    from src.utils.rag_database import get_reference_sources as get_rag_reference_sources
    
    # Use hybrid approach from RAG database module
    return get_rag_reference_sources(risk_topic=risk_topic, use_rag=use_rag)

