---
date: 2026-11-09
category: Cybersecurity
status: draft
source: "https://thehackernews.com/2026/11/default-adminadmin-server-password.html"
---

# Default 'admin:admin' Server Password Helps Researchers Hack Two Automakers, Unlock and Start Cars

**Category:** Cybersecurity

**Original source:** https://thehackernews.com/2026/11/default-adminadmin-server-password.html

---

# The Hidden Danger: Default Passwords Put Connected Cars at Risk

In an era where our vehicles are increasingly integrated with our digital lives, a recent security discovery serves as a stark reminder that even the most advanced systems can be compromised by the simplest of oversights. Two security researchers have revealed that a failure to change a default administrative password allowed them to gain full control over the mobile applications of two major automotive brands.

### The Vulnerability
The researchers discovered that the backend login systems for these car manufacturers—which utilized the ForgeRock identity platform, now a part of Ping Identity—were left protected by the notoriously insecure "admin:admin" default credentials. 

By exploiting this oversight, the researchers were able to bypass standard security protocols. This access was not limited to minor account settings; it granted them the ability to compromise any customer account associated with those specific mobile apps. For owners of connected vehicles, the implications were significant: the researchers could remotely unlock doors and even start the engines of the affected cars.

### Why This Matters
This incident highlights a critical vulnerability in the supply chain of connected vehicle technology. While automotive manufacturers focus heavily on the engineering and software of the cars themselves, the security of the third-party identity management platforms that connect those cars to the cloud is equally vital. 

When a company integrates an identity platform into its ecosystem, the responsibility for securing that gateway is shared. Leaving a default password active on a server is a fundamental security failure, yet it remains a common entry point for attackers looking to exploit enterprise-grade systems. This breach demonstrates that a single weak link in the authentication chain can expose thousands of users to physical security risks, turning a digital account compromise into a real-world threat.

### What Remains to be Verified
While the core facts of the breach are clear, several details remain for readers to monitor as more information becomes available:
* **Specific Automakers:** The names of the two affected car brands have not been disclosed in the initial reports.
* **Scope of Impact:** It is currently unclear how many vehicles were potentially vulnerable or if any malicious actors exploited this flaw before the researchers discovered it.
* **Remediation Status:** While it is standard practice for researchers to report such flaws to vendors for patching, users should verify if their specific car manufacturer has issued any security updates or advisories regarding their mobile app authentication.

### Conclusion
The ability to start a car via a smartphone is a hallmark of modern convenience, but it requires a robust foundation of cybersecurity. This event underscores the necessity for rigorous security audits, even for third-party identity services. For now, vehicle owners should ensure their mobile apps are updated to the latest versions and remain vigilant regarding account security.

---

## Editor verification

- [ ] Verify facts against the original source.
- [ ] Check names, dates and statistics.
- [ ] Review copyright and image permissions.
- [ ] Approve before publishing.
