# 🚀 GitHub 깨끗하게 처음부터 올리기 (초기화 및 배포 가이드)

이전 작업에서 `node_modules`가 포함되어 푸시가 거절되었거나 기록이 꼬였을 때, **아무런 문제 없이 처음부터 다시 시작하는 가장 확실한 방법**입니다.

---

## 1단계: 기존 깃 기록 완전히 지우기 (초기화)
로컬 프로젝트 폴더(`.../disk-monitor`)에서 기존의 잘못된 깃 기록(`.git` 폴더)을 삭제하여 깨끗한 상태로 만듭니다.

- **방법 (터미널/CMD에서 입력)**:
  - (Windows CMD): `rmdir /s /q .git`
  - (PowerShell): `rm -rf .git`

---

## 2단계: 새로 초기화 및 코드 커밋
제가 만들어둔 `.gitignore` 파일 덕분에, 이제 `node_modules`나 `venv` 같은 무거운 파일들은 자동으로 제외됩니다.

```bash
# 1. 깃 다시 시작
git init

# 2. 모든 파일 추가 (이제 소스 코드만 가볍게 추가됩니다)
git add .

# 3. 깨끗한 첫 커밋 생성
git commit -m "Initial commit: clean source code"
```

---

## 3단계: 깃허브 저장소 연결 및 푸시
기존에 만든 저장소를 그대로 사용하되, 서버의 기록을 현재의 깨끗한 상태로 덮어씁니다.

```bash
# 1. 메인 브랜치 이름 설정
git branch -M main

# 2. 저장소 URL 연결 (본인의 레포 URL 입력)
git remote add origin https://github.com/higashiaka/disk-monitor.git

# 3. 강제 푸시 (거절되었던 이전 기록을 무시하고 새로 올립니다)
git push -u origin main --force
```

---

## 4단계: 자동 배포 태그 달기 (v1.0.0)
이제 깃허브 서버에서 자동으로 설치 파일(.exe)이 만들어지도록 태그를 푸시합니다.

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## 💡 확인 및 결과
- **성공 확인**: `git add .` 후 `git status`를 입력했을 때 `node_modules`가 보이지 않으면 성공입니다.
- **배포 확인**: 깃허브 페이지 상단의 **Actions** 탭에서 빌드가 돌아가는 것을 확인하고, 완료되면 **Releases** 탭에서 결과물을 다운로드하세요.
