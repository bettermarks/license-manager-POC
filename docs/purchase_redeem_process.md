# The License Ordering and License Redeeming Process in a MultiService Environment with a SPA

A typical scenario for the new License Manager would be built up of a single page app with some
(micro) services attached. The license ordering process could be something like described below:

```mermaid
sequenceDiagram
    autonumber
    actor Teacher Thomas Müller
    participant SPA
    participant OrderManager
    participant LicenseManager
    participant HierarchyProvider

    Teacher Thomas Müller-->>SPA: I want to purchase a license
    
    SPA->>+OrderManager: Please give me all possible products
    OrderManager->>-SPA: Sure! Here are the products: "Full access" (10 Euros per seat per month) and "Prime Number Book" (2 Euros per seat per month)

    SPA->>+HierarchyProvider: Please give me all the entities, I am in 
    HierarchyProvider->>-SPA: Sure! Your are in  'Class: 5A', 'Class: 6A' and 'School: Heinrich Schliemann Gym.'   

    Teacher Thomas Müller->>+SPA: Ok, I want to purchase a license for 'Class 5A', Full Access', 100 seats for 5 months
    SPA->>+OrderManager: Please give me the full price for a license: 'Full Access', 100 seats, 5 months
    OrderManager->>-SPA: Sure! The full price for 'Full Access', 100 seats, 5 months is 5000 Euros.
    
    Teacher Thomas Müller->>+SPA: Yes, I want that and I confirm all the 'General terms and conditions of business'!
    SPA->>+OrderManager: Please book a license for Teacher Thomas Müller: ('Class: 5A', 'Full Access', 100 seats, 5 months) for 5000 Euros total.
    OrderManager->>OrderManager: Ok, I will log that and prepare an invoice (will be sent by mail).
    OrderManager->>-SPA: You can now purchase the license 'Full Access', 100 seats, for 5 months.
    
    SPA->>+LicenseManager: Teacher (eid='thomas_mueller') purchases license for 'Class: 5A' 'Full Access', 100 seats, 5 months
    LicenseManager->>-SPA: Done! Up to 100 members of 'Class: 5A' will have 'Full Access' access for 5 months 
```

Redeeming a license could work like this:

```mermaid
sequenceDiagram
    autonumber
    actor Student Kevin
    participant SPA
    participant IDP  
    participant LicenseManager
    participant HierarchyProvider
```