---
date: 2026-11-17
category: Cybersecurity
status: draft
source: "https://thehackernews.com/2026/11/new-gitdoor-and-graphdoor-backdoors.html"
---

# New GitDoor and GraphDoor Backdoors Turn GitHub and SharePoint Into Covert C2 Channels

**Category:** Cybersecurity

**Original source:** https://thehackernews.com/2026/11/new-gitdoor-and-graphdoor-backdoors.html

---

# Operation ShadowCloud: How Hackers Are Weaponizing GitHub and SharePoint

In an alarming development for global cybersecurity, researchers have uncovered a sophisticated campaign targeting government entities across Asia and Africa. Dubbed "Operation ShadowCloud," this intrusion campaign utilizes two previously undocumented backdoors—GitDoor and GraphDoor—to turn trusted enterprise platforms into covert command-and-control (C2) infrastructure.

### The Rise of "Living-off-the-Cloud" Attacks
The campaign, identified by Kaspersky in early 2026, represents a growing trend in cyber espionage: the exploitation of legitimate, high-reputation services to mask malicious activity. By leveraging Microsoft SharePoint and GitHub, the attackers are able to blend their malicious traffic with standard business operations.

For security teams, this presents a significant detection challenge. Because GitHub and SharePoint are essential tools for modern government and corporate workflows, blocking these domains is rarely a viable option. When attackers use these platforms to send commands or exfiltrate data, the traffic appears benign to traditional firewalls and network monitoring tools, allowing the backdoors to operate undetected for extended periods.

### Why This Matters
The emergence of GitDoor and GraphDoor highlights a critical shift in how state-sponsored or advanced persistent threat (APT) actors conduct operations. By moving away from custom-built, easily identifiable infrastructure and toward widely used cloud services, attackers are effectively lowering the "noise" their operations create.

This strategy forces security professionals to rethink how they monitor cloud-based traffic. Relying on simple domain blocking is no longer sufficient when the attacker’s infrastructure is hosted on the very platforms an organization relies on for daily productivity.

### What Remains to be Verified
While the existence of these backdoors and their association with Operation ShadowCloud have been confirmed by Kaspersky, several technical details remain for security researchers to clarify. Readers should look for further updates regarding:

*   **Infection Vectors:** How the initial payloads are delivered to government systems before the backdoors are established.
*   **Technical Indicators:** Specific file hashes, registry keys, or anomalous API patterns that security teams can use to hunt for these backdoors within their own environments.
*   **Attribution:** While the campaign is active, further analysis is required to determine the specific threat actors behind these tools.

### Conclusion
Operation ShadowCloud serves as a stark reminder that the tools we trust most can be turned against us. As attackers continue to refine their ability to hide in plain sight, organizations must prioritize behavioral analysis and endpoint detection to identify the subtle signs of a compromise. Security teams are encouraged to monitor their cloud service logs closely for unusual activity that deviates from standard user behavior.

---

## Editor verification

- [ ] Verify facts against the original source.
- [ ] Check names, dates and statistics.
- [ ] Review copyright and image permissions.
- [ ] Approve before publishing.
