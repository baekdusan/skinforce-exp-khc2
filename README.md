# pseudoskin

파일 이름을 바꿀 필요X

브랜치 생성: git branch j(main에서 생성하기)
브랜치 이동: git checkout j
브랜치 원격 저장소에 반영: git push origin j

----- 작업 진행 후 -----

git add .
git commit -m "작업 내용 적기"

기준 브랜치로 이동: git checkout main
기준 브랜치와 병합: git merge j

??? 만약 되지 않는다 ??? -> 충돌이 난 경우

1. 모여서 해결하기
2. git add .
3. git commit -m "Resolve conflicts"
4. git push


----- 작업 완료 후 삭제 -----
로컬: git branch -d j
원격: git push origin -d j
