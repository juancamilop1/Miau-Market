# Dependencias de Frontend (Angular 20)

## Instalar Node.js
- Node.js 18+ (https://nodejs.org/)
- npm (viene con Node.js)

## Instalar dependencias del proyecto
```bash
npm install
```

## Dependencias Principales (automáticas desde package.json):

### Framework Angular 20:
- @angular/animations ^20.3.6
- @angular/common ^20.3.6
- @angular/compiler ^20.3.6
- @angular/core ^20.3.6
- @angular/forms ^20.3.6
- @angular/platform-browser ^20.3.6
- @angular/platform-browser-dynamic ^20.3.6
- @angular/platform-server ^20.3.6
- @angular/router ^20.3.6
- @angular/ssr ^20.3.6

### Librerías:
- chart.js ^5.0.2 (gráficos dashboard)
- rxjs ~7.8.0 (reactive programming)
- zone.js ~0.15.0 (change detection)
- express ^4.18.2 (SSR server)

### DevDependencies:
- @angular/cli ^20.3.5
- @angular-devkit/build-angular ^20.3.5
- @angular/compiler-cli ^20.3.6
- typescript ~5.7.2

## Ejecutar:
```bash
npx ng serve
```

## Ejecutar en red (celular):
```bash
npx ng serve --host 0.0.0.0
```
