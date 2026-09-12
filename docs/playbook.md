## Backend

### Ignore \_\_pycache\_\_

```
touch backend/.gitignore
```

Add in `.gitignore`

```
__pycache__/
*.py[cod]   # means ignore every file name ends with pyc, pyo, pyd
```

Remove these files from git, because we have already commit it

```
git rm -r --cached backend/**/__pycache__
```

## Frontend

### Init

- Node.js - JavaScript runtime required to run the frontend tooling.
npm — Comes bundled with Node.js and is a package manager for JavaScript/TypeScript projects.
- Yarn 4 - An alternative package manager for JavaScript/TypeScript projects. This project uses Yarn 4.
- Corepack - A package manager manager that manages Yarn,...

```
sudo dnf install nodejs

node --version
npm --version

sudo corepack enable
corepack prepare yarn@4 --activate

yarn --version

cd frontend
yarn create vite

echo 'nodeLinker: node-modules' > .yarnrc.yml
```