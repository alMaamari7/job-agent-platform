Ich würde deshalb in dieser Reihenfolge weiterarbeiten:
1. Source Access Layer fertig konzipieren.
   ReadCandidateDocument wird zu einem allgemeineren ReadCandidateSource. Der Agent bekommt eine Liste autorisierter CandidateSource-Objekte und ruft Quellen über source_id ab. Intern entscheiden wir je nach Typ, wie gelesen wird: PDF/DOCX/XLSX/TXT zunächst per Parser, später PDF zusätzlich multimodal, GitHub über ein eigenes Repository-Tool und Webseiten über ein Web-Tool. Wichtig bleibt: Der Agent interpretiert, der Source-Layer stellt nur die Originalinformationen möglichst verlustarm bereit.
    Was noch nicht Teil von Punkt 1 abgeschlossen ist:
    - normaler WebReader für beliebige URLs
    - bessere Behandlung sehr großer Repositories
    - private GitHub-Repositories mit Token
    - multimodale PDFs/Bilder
    
2. Die vier Markdown-Spezifikationen als echte Agent-Konfiguration integrieren.
   Wir bauen einen Loader, der CANDIDATE_CONTEXT_STANDARD, CANDIDATE_PROFILING_AGENT, SKILL... und OUTPUT_CONTRACT lädt. Sie werden nicht einfach blind zusammenkopiert, sondern nach Rolle verwendet: Standard = Regeln, Agent-Datei = Verhalten, Skill = Workflow, Output Contract = Ergebnisanforderungen. Der Agent soll ausdrücklich target-unabhängig arbeiten und keine Job-Fit-Entscheidungen treffen.    CANDIDATE_PROFILING_AGENT_v1.1
3. Interne strukturierte Datenmodelle definieren.
   Bevor mehrere Agents miteinander arbeiten, brauchen wir Verträge wie SourceRecord, ParsedSourceFacts, EvidenceRecord, Capability, Limitation, ProfileSectionPlan und CandidateContextResult. Das verhindert, dass Agents nur freie Texte untereinander austauschen. Besonders wichtig ist EvidenceRecord, weil deine Spezifikation Claims, Kontext, Support-Level und Source-Referenzen verlangt.    CANDIDATE_CONTEXT_STANDARD_v1.1
4. Den bisherigen einzelnen ProfilingAgent in spezialisierte Agents aufteilen.
   Für Version 1 würde ich zunächst vier Agents bauen:
   SourceAgent → EvidenceAgent → ProfileAgent → ValidationAgent.
   Nicht sofort sieben oder acht. Der SourceAgent verarbeitet alle autorisierten Quellen. Der EvidenceAgent extrahiert, normalisiert, konsolidiert und bewertet Claims. Der ProfileAgent erzeugt Candidate Context inklusive Capability Map und dynamischer Sections. Der ValidationAgent kontrolliert Vollständigkeit, Evidence-Verknüpfungen, Kontexttreue und Regelverletzungen.
5. Einen deterministischen ProfilingManager bauen.
   Der Manager entscheidet nicht kreativ, sondern steuert die Reihenfolge:
   Sources → Evidence → Profile → Validation.
   Er prüft zusätzlich, ob alle autorisierten Quellen tatsächlich verarbeitet wurden. Deine Spezifikation verlangt genau das als Abschlusskriterium.    CANDIDATE_PROFILING_AGENT_v1.1
6. Candidate Context wirklich als Dateien erzeugen.
   Erst dann schreiben wir PROFILE.md, SOURCE_INDEX.md, EVIDENCE_INDEX.md, CAPABILITY_MAP.md, LIMITATIONS.md und profile/*.md. Dabei darf profile/ dynamisch bleiben; Abschnittsnamen und Anzahl hängen vom tatsächlichen Kandidaten ab.    CANDIDATE_CONTEXT_OUTPUT_CONTRA…
7. Technische Validatoren ergänzen.
   Nicht alles dem ValidationAgent überlassen. Python sollte deterministisch prüfen: existieren alle Pflichtdateien, referenziert jede CAP_### gültige EV_###, jede Evidence gültige SRC_###, wurden alle Quellen verarbeitet und gibt es ungültige Target-Role-Inhalte? Das ist wesentlich zuverlässiger als reine LLM-Selbstkontrolle.
8. Danach erst Source-Fähigkeiten erweitern.
   Zuerst GitHub-Repositories, dann normale Webseiten, später komplexere PDFs/Bilder. Repository-Analyse ist explizit Teil deines vorgesehenen Workflows: Sourcecode, Struktur, Dependencies, Dokumentation, Tests, Commit-Historie und Features können relevant sein.    SKILL_CANDIDATE_PROFILING_AGENT…
9. Danach Persistenz und Update-Modus.
   Unsere JSON-Registry ersetzen wir später durch DB-Modelle. Dann implementieren wir auch UPDATE_EXISTING_PROFILE, stabile SRC_###/EV_### IDs und inkrementelle Updates, statt jedes Profil komplett neu aufzubauen. Genau dieses Verhalten ist bereits in deiner Skill-Datei vorgesehen.    SKILL_CANDIDATE_PROFILING_AGENT…
10. Zum Schluss Evaluation.
       Wir testen verschiedene Kandidatenprofile und messen nicht nur, ob der Output „gut klingt“, sondern z. B. Source Coverage, unbelegte Claims, korrekte Support-Level, Evidence-Linkage, Kontextfehler und ausgelassene Informationen.