# 10 — Frontend Architecture

> Владелец: Architect / Frontend Lead
> Последнее обновление: 2026-02-19

---

## Бизнес-контекст

80%+ трафика — мобильный. Первое впечатление — видео-лендинг продавца из поисковика или соцсетей. Если страница грузится > 2 сек — пользователь уходит. Фронтенд должен быть быстрым, SEO-friendly и работать на слабых устройствах.

---

## Три приложения

| Приложение | Аудитория | Приоритет | Описание |
|-----------|----------|-----------|----------|
| **Buyer App** | Покупатели | P0 | Каталог, поиск, карточка товара, видео-лендинги, корзина, checkout, заказы |
| **Seller Dashboard** | Продавцы | P0 | Управление магазином, товарами, заказами, аналитика, видео-конструктор |
| **Admin Panel** | Операторы | P1 | Модерация, финансы, поддержка, настройки платформы |

---

## Стек и ADR

### ADR-F01: Next.js (App Router) как основной фреймворк
- [ ] 🔴 **Решение:** Next.js с App Router
- **Контекст:** SSR/SSG для SEO видео-лендингов и каталога. React Server Components для уменьшения JS bundle. Streaming SSR для быстрого FCP. Встроенный image optimization
- **Альтернативы:** Nuxt (меньше экосистема), Remix (слабее SSG), SvelteKit (меньше специалистов)

### ADR-F02: Монорепа — фронтенд внутри общей репы
- [ ] 🔴 **Решение:** `apps/` директория в корне монорепы, shared UI в `packages/ui/`
- **Контекст:** Общие proto-типы, единый CI, атомарные изменения API + фронтенд
- **Инструмент:** Turborepo для build orchestration фронтенд-части

### ADR-F03: Tailwind CSS + Radix UI как UI foundation
- [ ] 🔴 **Решение:** Tailwind для стилей, Radix UI для accessible primitives
- **Контекст:** Tailwind — утилитарный, минимальный CSS output, purge неиспользуемого. Radix — headless, accessible из коробки, не навязывает стиль
- **Альтернативы:** Shadcn/UI поверх Radix (рассмотреть), MUI (тяжелый, не нужен), Chakra (хуже tree-shaking)

### ADR-F04: Zustand для client state, TanStack Query для server state
- [ ] 🔴 **Решение:** Zustand (client) + TanStack Query (server cache)
- **Контекст:** Zustand — минимальный (1KB), без boilerplate. TanStack Query — кэширование, дедупликация запросов, optimistic updates. Не нужен Redux — оверкил для этого проекта
- **Пересмотр:** Если state станет сложным (> 20 stores), оценить другие решения

### ADR-F05: TypeScript strict mode
- [ ] 🔴 **Решение:** TypeScript с `strict: true`, `noUncheckedIndexedAccess: true`
- **Контекст:** На 10M users баги стоят дорого. Строгая типизация ловит ошибки до продакшена

---

## Структура в монорепе

```
apps/
├── buyer/                    # Next.js — покупательское приложение
│   ├── app/                  #   App Router pages
│   │   ├── (marketing)/      #     Лендинги, SEO страницы (SSG)
│   │   ├── (shop)/           #     Каталог, поиск, карточка (SSR)
│   │   ├── (checkout)/       #     Корзина, оформление (client)
│   │   ├── (account)/        #     Профиль, заказы, настройки
│   │   └── seller/[slug]/    #     Видео-лендинг продавца (SSG/ISR)
│   ├── components/           #   Компоненты специфичные для buyer
│   ├── hooks/                #   Custom hooks
│   ├── lib/                  #   API клиент, утилиты
│   └── public/               #   Статика
│
├── seller/                   # Next.js — дашборд продавца
│   ├── app/
│   │   ├── (dashboard)/      #     Обзор, метрики
│   │   ├── (products)/       #     Управление товарами
│   │   ├── (orders)/         #     Управление заказами
│   │   ├── (store)/          #     Настройка магазина, видео-конструктор
│   │   └── (analytics)/      #     Аналитика продаж
│   ├── components/
│   ├── hooks/
│   └── lib/
│
└── admin/                    # Next.js — админ-панель (Phase 1)
    └── ...

packages/
├── ui/                       # Shared UI kit (Radix + Tailwind)
│   ├── components/           #   Button, Input, Modal, Card, VideoPlayer...
│   ├── tokens/               #   Design tokens: colors, spacing, typography
│   └── index.ts
│
├── api-client/               # Typed API client (сгенерированный из OpenAPI)
│   ├── generated/            #   Auto-generated types и fetch functions
│   └── index.ts
│
└── shared/                   # Shared utilities
    ├── validators/            #   Zod schemas (переиспользуются в формах и API)
    ├── formatters/            #   Цены, даты, числа
    └── constants/             #   Enum-ы, маршруты, конфиг
```

---

## Страницы и экраны

### Buyer App

| Страница | Рендеринг | Performance Budget | Статус |
|----------|----------|-------------------|--------|
| **Главная** (каталог + рекомендации) | SSR + streaming | LCP < 1.5s, CLS < 0.1 | 🔴 |
| **Поиск** + фильтры | SSR (query) + client (фильтры) | Результат < 200ms, FID < 100ms | 🔴 |
| **Карточка товара** | SSR + ISR (revalidate 60s) | LCP < 2s, видео autoplay < 1s | 🔴 |
| **Видео-лендинг продавца** | SSG + ISR (revalidate 5min) | LCP < 1.5s, FCP < 0.8s | 🔴 |
| **Категория** | SSR + ISR | LCP < 2s | 🔴 |
| **Корзина** | Client-side | INP < 200ms | 🔴 |
| **Checkout** (2 шага) | Client-side, prefetch payment | TTI < 2s | 🔴 |
| **Регистрация / Логин** | Client-side | TTI < 1.5s | 🔴 |
| **Профиль / Заказы** | Client-side (auth protected) | FCP < 1s | 🔴 |
| **Трекинг заказа** | Client-side + WebSocket | Real-time обновления | 🔴 |
| **Отзывы** (форма + список) | SSR (список) + client (форма) | — | 🔴 |

### Seller Dashboard

| Страница | Описание | Статус |
|----------|---------|--------|
| **Обзор** | GMV сегодня, заказы, просмотры, графики за неделю/месяц | 🔴 |
| **Товары** — список | Таблица с поиском, фильтрами, bulk actions | 🔴 |
| **Товары** — создание/редактирование | Форма: фото, видео, варианты, цены, описание | 🔴 |
| **Товары** — bulk import | Upload CSV/Excel, mapping колонок, preview, confirm | 🔴 |
| **Заказы** — список | Фильтры по статусу, дате, поиск по номеру | 🔴 |
| **Заказы** — деталь | Состав, покупатель, статус, actions (confirm, ship, cancel) | 🔴 |
| **Магазин** — настройки | Название, описание, лого, контакты | 🔴 |
| **Магазин** — видео-конструктор | Drag-n-drop секции: hero video, товары, USP, отзывы, CTA | 🔴 |
| **Аналитика** | Просмотры, конверсия, top товары, источники трафика | 🔴 |
| **Финансы** | Баланс, история выплат, комиссии, вывод средств | 🔴 |
| **Промо** | Создание скидок, купонов, flash sales | 🔴 |

### Admin Panel (Phase 1)

| Страница | Описание | Статус |
|----------|---------|--------|
| **Модерация** — очередь | Товары/видео на проверку, approve/reject с причиной | 🔴 |
| **Пользователи** | Поиск, блокировка, история действий | 🔴 |
| **Продавцы** — верификация | Очередь KYC, документы, approve/reject | 🔴 |
| **Заказы** — арбитраж | Disputed заказы, решения, refund | 🔴 |
| **Финансы** | Общий GMV, комиссии, payouts, reconciliation | 🔴 |
| **Контент** | Категории, баннеры, промо-страницы | 🔴 |

---

## Ключевые компоненты UI Kit (`packages/ui/`)

### TODO: определить и реализовать

#### Базовые
- [ ] 🔴 Button (variants: primary, secondary, ghost, danger; sizes: sm, md, lg)
- [ ] 🔴 Input, Textarea, Select, Checkbox, Radio, Switch
- [ ] 🔴 Modal / Dialog, Drawer (mobile bottom sheet)
- [ ] 🔴 Toast / Notifications
- [ ] 🔴 Skeleton loaders
- [ ] 🔴 Pagination, Infinite scroll

#### Каталог
- [ ] 🔴 ProductCard (image, title, price, rating, seller badge)
- [ ] 🔴 ProductGrid (responsive: 2 col mobile, 3 tablet, 4 desktop)
- [ ] 🔴 SearchBar (with autocomplete dropdown)
- [ ] 🔴 FilterPanel (category tree, price range, ratings, availability)
- [ ] 🔴 SortDropdown (relevance, price asc/desc, newest, popular)
- [ ] 🔴 CategoryBreadcrumbs

#### Видео
- [ ] 🔴 VideoPlayer (HLS, poster, play/pause, mute, fullscreen, quality switch)
- [ ] 🔴 VideoUploader (drag-n-drop, progress, preview, crop thumbnail)
- [ ] 🔴 VideoGallery (horizontal scroll, autoplay on hover)
- [ ] 🔴 VideoLandingHero (full-width video + overlay CTA)

#### Checkout
- [ ] 🔴 CartItem (image, qty stepper, remove, price)
- [ ] 🔴 CartSummary (subtotal, shipping, tax, total)
- [ ] 🔴 AddressForm (auto-complete, validation)
- [ ] 🔴 PaymentForm (Stripe Elements integration)
- [ ] 🔴 OrderConfirmation

#### Seller
- [ ] 🔴 DataTable (sortable, filterable, selectable rows, bulk actions)
- [ ] 🔴 StatsCard (number + trend arrow + sparkline)
- [ ] 🔴 Chart (line, bar — Recharts или lightweight альтернатива)
- [ ] 🔴 FileUploader (images: multi, drag-n-drop, preview, reorder)
- [ ] 🔴 RichTextEditor (описание товара — lightweight, без WYSIWYG монстров)
- [ ] 🔴 LandingBuilder (drag-n-drop секции, preview, publish)

---

## Performance

### Core Web Vitals целевые значения

| Метрика | Buyer (mobile) | Seller Dashboard | Admin |
|---------|---------------|-----------------|-------|
| LCP | < 1.5s | < 2.5s | < 3s |
| FID / INP | < 100ms | < 200ms | < 300ms |
| CLS | < 0.1 | < 0.15 | < 0.2 |
| TTFB | < 400ms | < 500ms | — |
| Bundle size (initial) | < 100KB gzip | < 150KB gzip | < 200KB gzip |

### TODO: Performance

- [ ] 🔴 Bundle analyzer: отслеживать размер каждого route bundle в CI
- [ ] 🔴 Image optimization: Next.js Image component, WebP/AVIF, srcset, lazy loading
- [ ] 🔴 Video: poster frame → autoplay muted → user interaction → sound. Без autoplay с звуком
- [ ] 🔴 Font loading: `font-display: swap`, preload critical fonts, subset кириллица + латиница
- [ ] 🔴 Code splitting: dynamic import для тяжелых компонентов (charts, editors, video player)
- [ ] 🔴 Prefetch: prefetch следующей вероятной страницы (hover на карточке → prefetch карточки товара)
- [ ] 🔴 Service Worker: офлайн shell для buyer app, кэш каталога (Phase 2)
- [ ] 🔴 Стратегия Third-party scripts: отложенная загрузка analytics, chat widgets после LCP

---

## SEO

### Критично для маркетплейса — органический трафик = бесплатные пользователи

- [ ] 🔴 Видео-лендинги продавцов — SSG с ISR, уникальный URL `/{seller-slug}`
- [ ] 🔴 Карточки товаров — SSR, structured data (Product schema, aggregateRating, offers)
- [ ] 🔴 Категории — SSR, canonical URLs, хлебные крошки
- [ ] 🔴 Sitemap: автогенерация для всех товаров, категорий, лендингов
- [ ] 🔴 Open Graph / Twitter Cards: каждая страница — title, description, image (или video для лендингов)
- [ ] 🔴 Video SEO: VideoObject schema, video sitemap для Google Video Search
- [ ] 🔴 Мультиязычность: hreflang tags, URL strategy (subdomain vs path prefix)
- [ ] 🔴 robots.txt: закрыть checkout, профиль, admin от индексации
- [ ] 🔴 Page Speed: Google учитывает Core Web Vitals в ранжировании — бюджеты выше

---

## Mobile

### 80%+ трафика — мобильные устройства

- [ ] 🔴 Mobile-first responsive design. Desktop — адаптация, не наоборот
- [ ] 🔴 Touch targets: минимум 44x44px для интерактивных элементов
- [ ] 🔴 Bottom navigation bar для buyer app (главная, поиск, корзина, заказы, профиль)
- [ ] 🔴 Pull-to-refresh на списках
- [ ] 🔴 Swipe gestures: карусель фото товара, удаление из корзины
- [ ] 🔴 PWA manifest: install prompt, splash screen, standalone mode
- [ ] 🔴 Оптимизация для медленных сетей: skeleton screens, progressive image loading, offline fallback
- [ ] 🔴 Deep linking: ссылки из push/email открывают правильную страницу
- [ ] 🔴 Native app (Phase 3): React Native или Capacitor — решить позже, пока PWA

---

## API взаимодействие

### Typed API client

- [ ] 🔴 OpenAPI spec генерируется из FastAPI (backend) автоматически
- [ ] 🔴 TypeScript клиент генерируется из OpenAPI spec (`openapi-typescript-codegen` или `orval`)
- [ ] 🔴 Авто-обновление при изменении backend API в CI
- [ ] 🔴 TanStack Query wrappers вокруг сгенерированного клиента
- [ ] 🔴 Optimistic updates для корзины, лайков, отзывов
- [ ] 🔴 WebSocket клиент для: трекинг заказа, чат, real-time notifications

### Error handling на фронте

- [ ] 🔴 Global error boundary (React Error Boundary) с fallback UI
- [ ] 🔴 Per-route error boundaries для изоляции
- [ ] 🔴 Toast notifications для операционных ошибок (добавление в корзину, оплата)
- [ ] 🔴 Retry стратегия: автоматический retry для network errors (TanStack Query built-in)
- [ ] 🔴 Offline indicator + queue actions для отправки при восстановлении сети

---

## Интернационализация (i18n)

- [ ] 🔴 next-intl или next-i18next — определить библиотеку
- [ ] 🔴 Поддержка RTL (если целевые рынки требуют)
- [ ] 🔴 Формат: цены (валюта, разделители), даты, числа — через Intl API
- [ ] 🔴 Языки Phase 1: русский, английский
- [ ] 🔴 Стратегия: ключи в коде, переводы в JSON файлах, lazy load по locale

---

## Тестирование фронтенда

| Тип | Инструмент | Что тестируем | Когда |
|-----|-----------|--------------|-------|
| Unit | Vitest | Hooks, утилиты, форматтеры | Каждый PR |
| Component | Vitest + Testing Library | UI компоненты в изоляции | Каждый PR |
| Integration | Playwright | Критические flow (поиск → карточка → корзина → checkout) | Каждый PR |
| Visual regression | Playwright screenshots | UI не сломался после изменений | Каждый PR |
| Accessibility | axe-core + Playwright | WCAG 2.1 AA compliance | Еженедельно |
| Performance | Lighthouse CI | Core Web Vitals не деградировали | Каждый PR |

### TODO: Testing

- [ ] 🔴 Vitest + React Testing Library setup
- [ ] 🔴 Playwright setup с base fixtures (auth, seeded data)
- [ ] 🔴 Lighthouse CI в GitHub Actions: fail PR если LCP > budget
- [ ] 🔴 Storybook для UI Kit components (документация + visual testing)
- [ ] 🔴 Mock Service Worker (MSW) для тестов без реального API

---

## Фазовость

### Phase 0: MVP
- Buyer: главная, поиск, карточка товара, видео-лендинг, регистрация, корзина, checkout, заказы
- Seller: регистрация, добавление товаров, загрузка видео, список заказов, базовый лендинг
- UI Kit: базовые компоненты, VideoPlayer, ProductCard, формы
- Нет: admin panel, analytics charts, landing builder, i18n

### Phase 1: Launch
- Admin panel MVP (модерация, пользователи)
- Seller analytics (базовые графики)
- Push notifications (Web Push API)
- Buyer-seller чат (WebSocket)
- i18n: 2 языка

### Phase 2: Growth
- Landing builder (drag-n-drop конструктор)
- Advanced seller analytics (Recharts)
- A/B testing разных UI вариантов
- Performance optimization: Service Worker, advanced prefetching
- Short-form video feed (vertical scroll)

### Phase 3: Scale
- Native mobile app (React Native или Capacitor)
- Live shopping UI (video + chat + buy overlay)
- Visual search (photo → similar products)
- PWA offline mode
- 5+ языков
