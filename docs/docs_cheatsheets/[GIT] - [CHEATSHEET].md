# [GIT] - [CHEATSHEET]

## 0. Projektets Git-modell

Workspace:

```text
C:\Users\SSIRA\AI_Folder\workspaces\comfy_ui_workspace
```

Remote:

```text
origin → Sirak-K/c-ui-repo
```

Aktuell branchmodell:

```text
main
└── pg2/implementation
```

- `main` = skyddad/stabil baseline. Arbeta normalt **inte direkt på `main`**.
- `pg2/implementation` = aktuell PG-2-arbetsbranch.
- Det här projektet använder just nu **inte `develop`** som mellanbranch. Äldre exempel med `feature → develop → main` översätts här till **arbetsbranch → Pull Request → main**.
- ChatGPT kan göra remote-arbete på separat branch och öppna PR. Du hämtar sedan arbetet lokalt med `fetch` + `switch` + `pull`.

---

# 1. HÄMTA CHATGPT:S / REMOTE-ARBETE TILL LOKALT

## 1.1 Gå till workspace

```bash
cd /c/Users/SSIRA/AI_Folder/workspaces/comfy_ui_workspace
```

Går till det lokala Git-repot.

## 1.2 Kontrollera att arbetsytan är ren

```bash
git status
```

Visar aktuell branch samt staged, unstaged och untracked filer. Byt helst inte branch med oavsiktliga lokala ändringar.

## 1.3 Hämta senaste informationen från GitHub

```bash
git fetch origin
```

Hämtar nya commits och remote-branches från GitHub utan att ändra dina lokala filer eller din aktuella branch.

## 1.4 Se branches

```bash
git branch
git branch -a
```

- `git branch` visar lokala branches.
- `git branch -a` visar både lokala och remote-tracking branches.

## 1.5 Växla till `pg2/implementation`

Om branchen redan finns lokalt:

```bash
git switch pg2/implementation
```

Om den **inte** finns lokalt ännu:

```bash
git switch --track origin/pg2/implementation
```

Skapar en lokal branch som följer `origin/pg2/implementation` och växlar till den.

## 1.6 Hämta branchens senaste commits

```bash
git pull --ff-only
```

Uppdaterar den aktuella lokala branchen från dess remote-branch, men vägrar skapa en oväntad merge commit.

## 1.7 Kontrollera resultatet

```bash
git status
git log --oneline --graph --decorate -15
```

Bekräftar att du är på rätt branch och visar den senaste commit-historiken.

---

# 2. SNABBSEKVENS — DET DU BEHÖVER JUST NU

För att hämta aktuellt PG-2-arbete:

```bash
cd /c/Users/SSIRA/AI_Folder/workspaces/comfy_ui_workspace
git status
git fetch origin
git switch pg2/implementation
git pull --ff-only
git status
```

Om `git switch pg2/implementation` säger att branchen inte finns lokalt:

```bash
git switch --track origin/pg2/implementation
```

---

# 3. `FETCH` vs `PULL` vs `PUSH`

## `git fetch`

```bash
git fetch origin
```

Hämtar information och commits från GitHub men ändrar inte din aktuella lokala branch.

## `git pull`

```bash
git pull --ff-only
```

Hämtar remote-ändringar och uppdaterar den branch du står på. I detta projekt är `--ff-only` ett bra standardval för att undvika oavsiktliga merge commits.

## `git push`

```bash
git push
```

Skickar dina lokala commits till den remote-branch som din lokala branch följer.

Första gången en ny lokal branch pushas:

```bash
git push -u origin pg2/<branch-namn>
```

`-u` kopplar den lokala branchen till motsvarande remote-branch så framtida `git push` och `git pull` kan användas utan extra branchnamn.

---

# 4. NORMALT LOKALT ARBETSFLÖDE

## 4.1 Kontrollera status

```bash
git status
```

Se vad som har ändrats innan du stage:ar eller committar.

## 4.2 Stage:a ändringar

Alla ändringar:

```bash
git add .
```

Eller hellre specifika filer när du vill ha kontroll:

```bash
git add tools/pg2_bionic_native_audit.py
```

Lägger valda ändringar i staging area inför nästa commit.

## 4.3 Skapa commit

```bash
git commit -m "PG-2: harden Bionic native audit"
```

Skapar en lokal commit av det som ligger i staging area.

## 4.4 Push till GitHub

```bash
git push
```

Skickar committen/commitsen till branchens remote-motsvarighet.

---

# 5. SKAPA EN NY ARBETSBRANCH FRÅN `main`

Använd när ett nytt tydligt arbetsområde ska börja.

## 5.1 Börja från uppdaterad `main`

```bash
git status
git switch main
git fetch origin
git pull --ff-only origin main
```

Säkerställer att den nya branchen byggs från aktuell remote-`main`.

## 5.2 Skapa och växla till ny branch

```bash
git switch -c pg2/<kort-beskrivning>
```

Exempel:

```bash
git switch -c pg2/bionic-runtime-verification
```

`-c` skapar branchen och växlar direkt till den.

## 5.3 Publicera branchen

```bash
git push -u origin pg2/bionic-runtime-verification
```

Skapar remote-branchen och sätter upstream.

---

# 6. BYTA BRANCH SÄKERT

## Ren working tree

```bash
git status
git switch main
```

Om arbetsytan är ren kan du normalt växla direkt.

## Ocommittade ändringar som du vill spara tillfälligt

```bash
git stash
git switch <annan-branch>
```

`git stash` lägger undan ocommittade ändringar så branch-bytet kan göras med ren arbetsyta.

Ta tillbaka dem senare:

```bash
git stash pop
```

## Viktigt

- Ocommittade ändringar kan följa med vid branch-byte om Git kan göra det säkert.
- Om ändringarna krockar med målbranchen stoppar Git branch-bytet.
- Commits hör till den branch där de skapades.

---

# 7. UPPDATERA EN ARBETSBRANCH FRÅN REMOTE

När ChatGPT eller du själv har pushat nya commits till samma branch från en annan miljö:

```bash
git status
git fetch origin
git switch pg2/implementation
git pull --ff-only
```

Detta är standardsekvensen för vårt pågående arbetssätt.

---

# 8. SE VAD SOM SKILJER BRANCHEN FRÅN `main`

## Commit-lista

```bash
git log --oneline main..pg2/implementation
```

Visar commits som finns på PG-2-branchen men inte på lokal `main`.

## Översikt av filändringar

```bash
git diff --stat main...pg2/implementation
```

Visar vilka filer som skiljer sig och ungefär hur stor diffen är.

## Full diff

```bash
git diff main...pg2/implementation
```

Visar faktiska kod-/textändringar mellan `main` och arbetsbranchen.

> Kör `git fetch origin` först om du vill jämföra mot färsk remote-information.

---

# 9. PULL REQUEST — PROJEKTETS NORMALA INTEGRATIONSVÄG

En Pull Request är en begäran att integrera alla relevanta commits från en arbetsbranch in i `main`.

För vårt projekt:

```text
pg2/implementation
        ↓
Pull Request
        ↓
granskning / runtime-verifiering
        ↓
merge
        ↓
main
```

Git-operationerna före PR är normalt:

```bash
git status
git add .
git commit -m "<tydligt meddelande>"
git push
```

Själva PR:n skapas/hanteras på GitHub. I vårt arbetssätt kan ChatGPT normalt skapa och uppdatera PR:n remote.

### Draft PR

En PR kan ligga som **Draft** medan implementationen fortfarande verifieras. Den kan senare markeras **Ready for review**.

### Merge-metoder

GitHub kan typiskt erbjuda:

- **Merge commit** — bevarar branchens commits och skapar en merge commit.
- **Squash merge** — gör PR:ns ändringar till en enda commit på `main`.
- **Rebase merge** — flyttar commits linjärt ovanpå målbranchen.

För stora experiment-/implementationsbrancher är **Squash merge** praktiskt när `main` ska få en ren slutcommit.

---

# 10. EFTER ATT EN PR HAR MERGATS TILL `main`

## 10.1 Uppdatera lokal `main`

```bash
git switch main
git fetch origin
git pull --ff-only origin main
```

Nu motsvarar lokal `main` den nya remote-baslinjen.

## 10.2 Ta bort gammal lokal arbetsbranch

Försök först säkert:

```bash
git branch -d pg2/implementation
```

`-d` vägrar om Git inte anser branchen mergad.

Efter en **squash merge** kan Git fortfarande vägra eftersom de ursprungliga branch-commitsen inte finns ordagrant på `main`. Om du redan har verifierat att PR:n är mergad och inte behöver den lokala branchen:

```bash
git branch -D pg2/implementation
```

`-D` tvingar lokal borttagning. Använd endast efter att merge/resultat har verifierats.

## 10.3 Ta bort remote-branchen

```bash
git push origin --delete pg2/implementation
```

Tar bort arbetsbranchen på GitHub när den inte längre behövs.

---

# 11. LOKAL MERGE — TEORETISKT / SÄLLAN BEHÖVD HÄR

```bash
git switch main
git merge pg2/implementation
```

Kombinerar arbetsbranchens commits in i lokal `main`.

I detta projekt föredrar vi normalt **Pull Request → merge på GitHub** framför direkt lokal merge, eftersom PR:n ger en tydlig gransknings- och beslutsgräns.

Efter en medveten lokal merge skulle remote uppdateras med:

```bash
git push origin main
```

Direkt push till `main` är dock inte vårt normala arbetsflöde.

---

# 12. ÄNDRA SENASTE COMMIT

## Lägg till något i senaste commit / ändra commit message

```bash
git commit --amend
```

Omskriver den senaste lokala committen.

Om committen redan är pushad innebär amend att commit-historiken ändras. Undvik att skriva om delad historik utan ett tydligt skäl.

---

# 13. ÅNGRA SENASTE LOKALA COMMIT MEN BEHÅLL ÄNDRINGARNA

```bash
git reset --soft HEAD~1
```

Tar bort senaste committen från historiken men lämnar ändringarna staged så de kan justeras och committas igen.

---

# 14. REBASE — KÄNN TILL, MEN INTE STANDARD HÄR

```bash
git rebase main
```

Flyttar den aktuella branchens commits så att de läggs ovanpå `main`.

Bra för linjär historik men omskriver commit-ID:n. Det är inte ett krav i vårt normala PG-2-flöde.

Interaktiv variant:

```bash
git rebase -i HEAD~3
```

Kan t.ex. squash:a eller ändra de senaste commitsen. Vanligtvis enklare att använda GitHubs **Squash merge** för vårt projekt.

---

# 15. CHERRY-PICK — SPECIALFALL

```bash
git cherry-pick <commit-hash>
```

Kopierar en specifik commit till den branch du står på.

Inte del av normalflödet; använd endast när just en enskild commit medvetet behöver flyttas mellan branches.

---

# 16. TAGGAR — VERSION / MILESTONE

Skapa en tagg:

```bash
git tag v1.0.0
```

Push taggen:

```bash
git push origin v1.0.0
```

Används när du vill märka en särskild commit/version. Inte nödvändigt för den aktuella PG-2-branchsynkningen.

---

# 17. KOMPAKT KOMMANDOREFERENS

| Kommando                               | Vad det gör                                              |
| -------------------------------------- | -------------------------------------------------------- |
| `git status`                           | Visar branch och lokal ändringsstatus.                   |
| `git fetch origin`                     | Hämtar remote-information utan att ändra working tree.   |
| `git branch`                           | Visar lokala branches.                                   |
| `git branch -a`                        | Visar lokala + remote branches.                          |
| `git switch <branch>`                  | Växlar branch.                                           |
| `git switch --track origin/<branch>`   | Skapar lokal tracking-branch från remote.                |
| `git switch -c <branch>`               | Skapar och växlar till ny lokal branch.                  |
| `git pull --ff-only`                   | Uppdaterar aktuell branch utan oväntad merge commit.     |
| `git add .`                            | Stage:ar alla ändringar.                                 |
| `git add <fil>`                        | Stage:ar vald fil.                                       |
| `git commit -m "..."`                  | Skapar lokal commit.                                     |
| `git push`                             | Pushar commits till upstream-branch.                     |
| `git push -u origin <branch>`          | Första push + sätter upstream.                           |
| `git stash`                            | Lägger undan ocommittade ändringar tillfälligt.          |
| `git stash pop`                        | Återställer senaste stash.                               |
| `git log --oneline --graph --decorate` | Visar kompakt commit-historik.                           |
| `git diff main...<branch>`             | Visar branchens skillnad mot `main`.                     |
| `git merge <branch>`                   | Mergar branch in i aktuell branch lokalt.                |
| `git branch -d <branch>`               | Säker lokal branch-radering.                             |
| `git branch -D <branch>`               | Tvingad lokal branch-radering.                           |
| `git push origin --delete <branch>`    | Tar bort remote-branch.                                  |
| `git commit --amend`                   | Ändrar senaste commit.                                   |
| `git reset --soft HEAD~1`              | Tar bort senaste commit men behåller ändringarna staged. |
| `git rebase main`                      | Flyttar branchens commits ovanpå `main`.                 |
| `git cherry-pick <hash>`               | Kopierar en specifik commit till aktuell branch.         |

---

# 18. VÅRA VANLIGASTE WORKFLOWS

## A. ChatGPT har gjort nytt arbete på `pg2/implementation`

```bash
git status
git fetch origin
git switch pg2/implementation
git pull --ff-only
```

Om branchen saknas lokalt:

```bash
git switch --track origin/pg2/implementation
```

## B. Du gör en lokal ändring på aktuell PG-2-branch

```bash
git status
git add <ändrade-filer>
git commit -m "PG-2: <kort beskrivning>"
git push
```

## C. Starta nytt isolerat arbete

```bash
git switch main
git fetch origin
git pull --ff-only origin main
git switch -c pg2/<nytt-arbete>
git push -u origin pg2/<nytt-arbete>
```

## D. PR har mergats och du vill tillbaka till aktuell baseline

```bash
git switch main
git fetch origin
git pull --ff-only origin main
git status
```

## E. Du måste byta branch mitt i ocommittat arbete

```bash
git stash
git switch <annan-branch>
```

Tillbaka senare:

```bash
git switch <ursprunglig-branch>
git stash pop
```

---

# 19. MENTAL MODELL

```text
Working Directory
      ↓ git add
Staging Area
      ↓ git commit
Local branch
      ↓ git push
Remote branch (GitHub)
      ↓ Pull Request + merge
main på GitHub
      ↓ git fetch + git pull
lokal main
```

Det viktigaste i vårt nuvarande projekt är därför:

```text
fetch → switch → pull
        ↓
   arbeta/testa
        ↓
add → commit → push
        ↓
 Pull Request
        ↓
      merge
        ↓
switch main → pull
```
