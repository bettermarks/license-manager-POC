# Communication between an SPA and multiple services

In our 'licensing' scenario, we have some services, that can be separated from each other, but have
to 'communicate' with each other, either directly or using some 'indirect' way

## Direct Service-Service Communication with an SPA

### Purchasing a license
```mermaid
flowchart TD
SPA(SPA)-->ORDS(Ordering Service);
ORDS(Ordering Service)-->LICS(Licensing Service);
ORDS(Ordering Service)-->HIPS(Hierarchy Provider Service);
LICS(Licensing Service)-->HIPS(Hierarchy Provider Service);
```

### Redeeming a license
```mermaid
flowchart TD
LICS(Licensing Service)-->HIPS(Hierarchy Provider Service);
SPA(SPA)-->APP(The application itself);
APP(The application itself)-->LICS(Licensing Service)
```

## Indirect Service-Service Communication with an SPA (using signed messages)

### Purchasing a license

```mermaid
flowchart TB
SPA(SPA)-->ORDS(Ordering Service);
SPA(SPA)-->LICS(Licensing Service);
SPA(SPA)-->HIPS(Hierarchy Provider Service);
ORDS(Ordering Service) -.- |trusts| LICS(Licensing Service);
LICS(Licensing Service) -.- |trusts| HIPS(Hierarchy Provider Service);
ORDS(Ordering Service) -.- |trusts| HIPS(Hierarchy Provider Service);
```

### Redeeming a license
```mermaid
flowchart TD
SPA(SPA)-->APP(The application itself);
SPA(SPA)-->LICS(Licensing Service);
SPA(SPA)-->HIPS(Hierarchy Provider Service);
APP(The application itself) -.- |trusts| LICS(Licensing Service);
LICS(Licensing Service) -.- |trusts| HIPS(Hierarchy Provider Service);
APP(The application itself) -.- |trusts| HIPS(Hierarchy Provider Service);
```

Questions:

- PROs and CONs of each alterntive
- How could 'trust' be implemented?
    - Shared secret to sign messages.
    - Public/private key pairs for every service to sign messages.
    - ?
- Are there any other alternatives?