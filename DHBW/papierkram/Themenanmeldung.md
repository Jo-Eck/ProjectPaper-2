# Zweite Iteration der Themenanmeldung

## Projekt titel

Development and demonstration of a proof-of-concept for the integration of programming frameworks for high performance computing into a container-based workflow orchestrator.

## Problem Definition

> Describe the present problem that you are supposed to work on. Show that the problem definition is current, interesting, and complex enough, has high practical relevance, and will also meet scientific standards.

Im Bereich der Hochleistungsrechnung besteht aktuell ein Bedarf für robuste Workflow-Management Werkzeuge.
Dieser Bedarf speist sich aus der zunehmenden Komplexität der Daten und der daraus resultierenden Prozesse, welche diese Daten verarbeiten. \
Um diese Komplexität zu bewältigen bedarf es zum einen einer Automatisierung und Abstraktion der alltäglichen Aufgaben welche für die Instandhaltung dieser Datensätze und deren Endprodukte nötig sind. \
Prozesse, welche in der Softwareentwickelung bereits seit Jahren etabliert sind, wie z.B. Versionierung, automatisierte Tests und die darauf folgende Integration in die Produktivumgebung, werden nun auch für die Verwaltung von Daten immer wichtiger. \
Deshalb entstehen nun auf dem Markt einige Produkte, welche versuchen sich in den Bereichen MlOps und DataOps zu etablieren.

Viele dieser Werkszeuge spezialisieren sich jedoch auf die Anforderungen der Machine Learning Community, welche nur ein Teilbereich der Hochleistungsrechnung ist.
Diese Orchestratoren sind meistens auf die Verarbeitung von Daten innerhalb von Containern ausgelegt, diese die Verwaltung von Abhängigkeiten und die Isolation von Prozessen erleichtern. \
Um diese Werkzeuge auch für andere Bereiche der Forschung und Industrie attraktiv zu machen, bedarf es der Integration von klassischen Hochleistungsrechen-Frameworks.
Diese fuer Hochleistungsrechner entwickelten Frameworks sind jedoch historisch bedingt nicht auf Container sondern ausgelegt, sonder arbeiten mit bare-metal Job-Schedulern wie Slurm. \
Eine Integration  dieser Frameworks, wie beispielsweise Chapel oder Julia, in ein containerbasiertes Workflow Management Tool könnte helfen diese Lücke zwischen den beiden Welten zu schließen und die Vorteile beider Ansätze zu vereinen.

Um dieses Problem zu adressieren, soll nun im Rahmen der Projektarbeit ein Proof of Concept entwickelt werden, welcher anhand einer beispielhaften Workflow-Pipeline die Integration eines Hochleistungsrechnungsframeworks in ein Workflow Management Tool demonstriert.

Dabei gilt es besonders den daraus resultierend Overhead zu betrachten, welcher durch die verschiedenen Abstraktionslagen wie Containerisierung und die  Differenzierung der einzelnen Komponenten in Microservices entsteht uns dieses mit den Vorteilen durch die Skalierbarkeit und die automatisierte Verwaltung der einzelnen Komponenten abzuwägen.

## Ziele der Arbeit

Das Ziel der Arbeit ist es, die Herausforderungen und Anforderungen zu analysieren, die bei der Integration eines Hochleistungsrechnungsframeworks in ein containerbasiertes Workflow-Management-Tool auftreten. \
Diese Analyse wird der erste Schritt sein, um ein tieferes Verständnis der bestehenden Probleme und Bedürfnisse zu gewinnen. \
Auf der Grundlage dieser Analyse wird ein Proof of Concept (PoC) entwickelt und implementiert, der die Machbarkeit und Effektivität einer solchen Integration zeigt. Dieser PoC wird auf seine Leistung, den Overhead und seine praktische Nutzbarkeit bewertet, um die Vorteile und Nachteile eines solchen Ansatzes zu ermitteln.

Ein weiteres Ziel der Arbeit ist es, potenzielle Verbesserungen und zukünftige Forschungsrichtungen zu identifizieren.

Die Forschungsfrage, die diese Arbeit beantworten soll, ist dreifach:

1. Wie kann ein Hochleistungsrechnungsframework effektiv in ein containerbasiertes Workflow-Management-Tool integriert werden?
2. Inwiefern beeinflusst die Nutzung eines containerbasierten Workflow-Management-Tools die Leistung des Hochleistungsrechners?
3. Welche Möglichkeiten zur Verbesserung der Integration von Hochleistungsrechenframeworks in containerbasierte Workflow-Management-Tools gibt es?

Die Beantwortung dieser Fragen wird dazu beitragen, die bestehende Lücke zwischen der Hochleistungsrechen- und der containerbasierten Welt zu überbrücken und so die Vorteile beider Ansätze zu nutzen.

## Methodik

Um die oben genannten Fragen zu beantworten und ein Artefakt zu kreieren wird ein iterativer Prozess verfolgt, welcher sich an den Prinzipien des Design Thinking orientiert.
Dabei werden 5 Phasen durchlaufen, welche eine kontinuierliche Verbesserung des Artefakts ermöglichen.

### Nutzerbedürfnisse verstehen

Zuerst wird sich mit den zukünftigen Nutzern des Artefakts auseinandergesetzt. Dabei handelt es sich um die Forscher und Entwickler, des Hewlett Packard Enterprise (HPE) Labors in Milpitas, Kalifornien. \
Diese werden in einem Interview befragt, um die Anforderungen an das Artefakt zu ermitteln. \
In zukünftigen Iterationen wird das Artefakt dann mit den Nutzern getestet, um anhand des Feedbacks die Anforderungen zu verfeinern.

### Erstellen eines Szenarios

Basierend auf den Anforderungen wird ein Szenario erstellt, welches den Entwickler in das Mindset des Nutzers versetzt. \
Dieses Szenario wird dann als Grundlage für die Entwicklung des Artefakts verwendet und dient gleichzeitig als eine demonstrierbare Anwendung.
In weiteren Iterationen kann dieses Szenario entweder erweitert oder durch ein neues ersetzt werden, welches einen anderen Anwendungsfall abdeckt um das Feature-set nuetzlich zu erweitern.

### Design des Artefakts

Nun kann basierend auf dem Szenario die Architektur des Artefakts entworfen werden. \
In dieser Phase treffen die Anforderungen des Nutzers auf die technischen Möglichkeiten und Einschränkungen. \
Hier werden die Entscheidungen darueber getroffen, welche technologischen Komponenten verwendet werden und wie diese miteinander interagieren sollen.
Bei weiteren Iterationen wird dieses Design dann verfeinert und an die neuen Anforderungen angepasst.

### Implementierung des Artefakts

In dieser Phase wird das Artefakt moeglichst nah zu dem Design aus der vorherigen Phase implementiert. \
Während dieser Integration wird sich zeigen an welchen Stellen neue Anforderungen entstehen und welche Anforderungen oder Designentscheidungen nicht wie erwartet funktionieren. \
Diese Erkenntnisse werden dabei in die naechste Iteration mitgenommen und dort beruecksichtigt.

Wichtig ist bei dieser phase auch die Dokumentation der einzelnen Schritte, um die Entscheidungen nachvollziehbar zu machen und die Ergebnisse reproduzierbar zu gestalten.
Diese Nachvollziehbarkeit ist nicht nur fuer Nutzer und Dritte wichtig, sondern auch fuer die eigene Arbeit da diese die Grundlage fuer die weiteren Iterationen bildet.

### Evaluation des Artefakts

Nun kann das Resultat anhand der gewonnenen Erkenntnisse evaluiert werden. \
Dabei wird nicht nur das Artefakt als solches betrachtet, sonder auch die zugrunde liegenden Annahmen welche wir bei der Erstellung des Szenarios und der Entwickelung des Designs getroffen haben. \
In diesem Schritt findet auch die Vorbereitung fuer die naechste Iteration statt, in der die gewonnenen Erkenntnisse in die Verbesserung des Artefakts mit einfliessen.

Dabei werden neue Aspekte und Anforderungen identifiziert, welche in den naechsten Iterationen beruecksichtigt werden muessen.

## Gliederung

1. Introduction
    - Problem Statement
    - Aim and Objectives
    - Research Questions
2. Methodology
    - Understanding User Needs
    - Scenario Creation
    - Artifact Design
    - Artifact Implementation
    - Artifact Evaluation
3. Related Work and Background
    - Workflow Management Tools
    - High Performance Computing Frameworks
    - Containerization
    - Microservices
4. Creation of the Artifact
    - User Needs
    - Design
    - Implementation
    - Evaluation
5. Conclusion
    - Summary
    - Future Work
6. References
7. Appendix

## Zeitplan

Woche 1-2: Einführung

    Problemstellung definieren
    Ziele und Aufgaben festlegen
    Forschungsfragen aufstellen

Woche 3-4: Methodik

    Nutzerbedürfnisse verstehen
    Szenario erstellen

Woche 5-7: Hintergrundarbeit und verwandte Arbeiten

    Workflow-Management-Tools 
    Hochleistungsrechen-Frameworks 
    Containerisierung & Mikroservices

Woche 8-9: Entwicklung des Artefakts - Benutzerbedürfnisse

    Durchführung von Interviews mit Benutzern
    Identifizierung von Benutzeranforderungen
    Synthese und Analyse der gesammelten Daten

Woche 10-11: Entwicklung des Artefakts - Design

    Auswahl der zu verwendenden Technologien
    Kozeptionierung des Systems und seiner Komponenten
    Planung der Interaktion zwischen den Komponenten

Woche 12-15: Entwicklung des Artefakts - Implementierung

    Codierung und Entwicklung des Systems
    Behebung von Problemen, die während der Implementierungsphase auftreten

Woche 16-17: Entwicklung des Artefakts - Bewertung

    Durchführung von Benutzertests
    Sammlung von Feedback
    Durchführung von Leistungstests

Woche 18-19: Schlussfolgerung

    Zusammenfassung der Ergebnisse
    Diskussion der Auswirkungen der Forschung
    Erörterung möglicher Verbesserungen und zukünftiger Forschungsrichtungen
    Erstellung des Abschlussberichts und der Präsentation

Woche 20: Pufferzeit

    Zeit für unerwartete Verzögerungen oder zusätzliche Arbeit

---

# English Version

## Project title

Development and demonstration of a proof-of-concept for the integration of programming frameworks for high performance computing into a container-based workflow orchestrator.

## Problem Definition

> Describe the present problem that you are supposed to work on. Show that the problem definition is current, interesting, and complex enough, has high practical relevance, and will also meet scientific standards.

There is a current need for robust workflow management tools in the area of high performance computing.
This need is driven by the increasing complexity of data and the resulting processes that handle this data. \
To cope with this complexity, automation and abstraction of the day-to-day tasks required to maintain these data sets and their end products is needed. \
Processes that have been established in software development for years, such as versioning, automated testing and subsequent integration into the production environment, are now becoming increasingly important for the management of data. \
As a result, a number of products are now emerging on the market that attempt to establish themselves in the areas of MlOps and DataOps.

However, many of these tools specialize in the needs of the machine learning community, which is only a subset of high-performance computing.
These orchestrators are mostly designed to process data within containers, these facilitate dependency management and process isolation. \
Making these tools attractive to other areas of research and industry requires the integration of classical high-performance computing frameworks.
However, these frameworks developed for high-performance computing have historically not been designed for containers, but instead work with bare-metal job schedulers such as Slurm. \
Integrating these frameworks, such as Chapel or Julia, into a container-based workflow management tool could help bridge this gap between the two worlds and combine the benefits of both approaches.

To address this problem, the project will develop a proof of concept that demonstrates the integration of a high-performance computing framework into a workflow management tool using an exemplary workflow pipeline.

In particular, the resulting overhead, which arises from the various abstraction layers such as containerization and the differentiation of the individual components into microservices, must be considered and weighed against the advantages of scalability and automated management of the individual components.

## Objectives of the work

The objective of the work is to analyze the challenges and requirements involved in integrating a high-performance computing framework with a container-based workflow management tool. \
This analysis will be the first step to gain a deeper understanding of the existing issues and needs. \
Based on this analysis, a Proof of Concept (PoC) will be developed and implemented to demonstrate the feasibility and effectiveness of such an integration. This PoC will be evaluated for its performance, overhead, and practicality to determine the advantages and disadvantages of such an approach.

Another goal of the thesis is to identify potential improvements and future research directions.

The research question that this thesis aims to answer is threefold:

1. how can a high-performance computing framework be effectively integrated into a container-based workflow management tool?
2. to what extent does the use of a container-based workflow management tool affect the performance of the high-performance computing framework?
3. what are the opportunities for improving the integration of high-performance computing frameworks with container-based workflow management tools?

Answering these questions will help bridge the existing gap between the high-performance computing and container-based worlds to take advantage of both approaches.

## Methodology

To answer the above questions and create an artifact an iterative process will be followed, which is based on the principles of design thinking.
This involves going through 5 phases that enable continuous improvement of the artifact.

### Understanding user needs

First, the future users of the artifact are addressed. These are the researchers and developers, of the Hewlett Packard Enterprise (HPE) lab in Milpitas, Calif. \
They will be interviewed to determine the requirements for the artifact. \
In future iterations, the artifact is then tested with users to refine requirements based on feedback.

### Creating a scenario

Based on the requirements, a scenario is created that puts the developer in the mindset of the user. \
This scenario is then used as the basis for the development of the artifact and also serves as a demonstratable application.
In further iterations, this scenario can either be extended or replaced by a new one that covers a different use case to usefully extend the feature set.

### Design of the artifact

Now, based on the scenario, the architecture of the artifact can be designed. \
In this phase, the user's requirements meet the technical possibilities and constraints. \
Decisions are made here about which technological components to use and how they should interact with each other.
In further iterations, this design is then refined and adapted to the new requirements.

### Implementation of the artifact

In this phase, the artifact is implemented as close as possible to the design from the previous phase. \
During this integration, it will become apparent where new requirements arise and which requirements or design decisions do not work as expected. \
These findings will be taken to the next iteration and considered there.

In this phase, it is also important to document the individual steps in order to make the decisions traceable and to make the results reproducible.
This traceability is important not only for users and third parties, but also for the company's own work, as it forms the basis for further iterations.

### Evaluation of the artifact

Now the result can be evaluated on the basis of the knowledge gained. \
Not only the artifact as such is considered, but also the underlying assumptions we made when creating the scenario and developing the design. \
This step also includes the preparation for the next iteration, in which the knowledge gained will be used to improve the artifact.

New aspects and requirements are identified, which must be considered in the next iterations.

## Outline

1. introduction
    - Problem Statement
    - Aim and Objectives
    - Research Questions
2. methodology
    - Understanding User Needs
    - Scenario Creation
    - Artifact Design
    - Artifact Implementation
    - Artifact Evaluation
3. Related Work and Background
    - Workflow Management Tools
    - High Performance Computing Frameworks
    - Containerization
    - microservices
4. Creation of the Artifact
    - User Needs
    - Design and
    - Implementation
    - Evaluation
5. conclusion
    - Summary of the
    - Future Work
6. references
7. appendix

## Schedule

Week 1-2: Introduction

    Define problem
    Establish goals and objectives
    Establish research questions

Week 3-4: Methodology

    Understand user needs
    Create scenario

Week 5-7: Background and related work

    Workflow management tools 
    High performance computing frameworks 
    Containerization & microservices

Week 8-9: Artifact development - user needs.

    Conducting interviews with users
    Identifying user requirements
    Synthesizing and analyzing the data collected

Week 10-11: Developing the artifact - design.

    Selection of technologies to be used
    Conceptualization of the system and its components
    Planning the interaction between the components

Week 12-15: Development of the artifact - implementation

    Coding and development of the system
    Troubleshooting issues that arise during the implementation phase

Week 16-17: Development of the artifact - evaluation

    Conducting user tests
    Collection of feedback
    Conducting performance tests

Week 18-19: Conclusion

    Summary of findings
    Discussion of the implications of the research
    Discussion of possible improvements and future research directions
    Preparation of the final report and presentation

Week 20: Buffer time.

    Time for unexpected delays or additional work