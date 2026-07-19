FROM node:22-alpine

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@10.17.1 --activate

COPY package.json pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile

COPY . .

ENV HOSTNAME=0.0.0.0
ENV PORT=3000

RUN pnpm build

EXPOSE 3000

CMD ["pnpm", "start"]
