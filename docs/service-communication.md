# Communication between an SPA and multiple services

In our 'licensing' scenario, we have some services, that can be separated from each other, but have
to 'communicate' with each other, either directly or using some 'indirect' way

## Direct Service-Service Communication with an SPA

### Purchasing a license
```mermaid
flowchart TD
ORDS(Ordering Service)
SPA(SPA)
HIPS(Hierarchy Provider Service)
LICS(Licensing Service)

SPA--> |SSO ???| ORDS;
ORDS-->LICS;
ORDS-->HIPS;
LICS-->HIPS;
```

### Redeeming a license
```mermaid
flowchart TD
SPA(SPA)
HIPS(Hierarchy Provider Service)
LICS(Licensing Service)
APP(protected content)

LICS-->HIPS;
SPA-->APP;
APP-->LICS
```

## Indirect Service-Service Communication with an SPA (using signed messages)

### Purchasing a license

```mermaid
flowchart TB
ORDS(Ordering Service)
SPA(SPA)
HIPS(Hierarchy Provider Service)
LICS(Licensing Service)

SPA--> |signed| ORDS;
SPA--> |signed| LICS;
SPA--> |SSO| HIPS;
ORDS -.- |trusts| LICS;
LICS -.- |trusts| HIPS;
ORDS -.- |trusts| HIPS;
```

### Redeeming a license
```mermaid
flowchart TD
APP(protected content)
LICS(Licensing Service)
HIPS(Hierarchy Provider Service)

SPA(SPA)-->APP;
SPA(SPA)--> |signed| LICS;
SPA(SPA)--> |SSO| HIPS;
APP -.- |trusts| LICS;
LICS -.- |trusts| HIPS;
APP -.- |trusts| HIPS;
```

Questions:

- PROs and CONs of each alterntive
- How could 'trust' be implemented?
    - Shared secret to sign messages.
    - Public/private key pairs for every service to sign messages.
    - ?
- Are there any other alternatives?