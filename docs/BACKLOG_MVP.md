# MVP Backlog (Blog)

## Epic 1: Auth & Accounts
- [ ] JWT auth (email/password)
- [ ] Role model: admin, editor, reader
- [ ] Admin login page
- [ ] Mobile login flow

## Epic 2: Posts
- [ ] Post schema (title, slug, content, status, tags, timestamps)
- [ ] CRUD API for posts
- [ ] Publish/unpublish endpoint
- [ ] Public posts list endpoint
- [ ] Post detail endpoint by slug

## Epic 3: Admin Dashboard
- [ ] Posts table
- [ ] Post editor
- [ ] Publish controls
- [ ] Basic analytics widgets

## Epic 4: Public Web
- [ ] Home feed
- [ ] Post details page
- [ ] Tag filtering
- [ ] SEO metadata + sitemap

## Epic 5: Mobile Flutter
- [ ] Auth
- [ ] Feed
- [ ] Post details
- [ ] Profile/settings shell

## Epic 6: Platform/Infra
- [ ] OpenTofu dev baseline (VPC, ECS, RDS, Redis, ECR)
- [ ] CI pipeline (lint/test/build)
- [ ] CD pipeline to dev ECS
- [ ] Observability baseline (CloudWatch + Sentry)
