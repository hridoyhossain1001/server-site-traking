# 🚀 Heroku থেকে DigitalOcean Migration নির্দেশিকা (Migration Guide)

এই গাইডে আমরা আপনার বর্তমান Heroku FastAPI অ্যাপ্লিকেশন এবং PostgreSQL ডাটাবেসকে **DigitalOcean-এর $12/মাস (2GB RAM, 1 vCPU) Droplet**-এ মাইগ্রেট করার পুরো প্রক্রিয়া বিস্তারিতভাবে আলোচনা করব।

---

## 📋 পূর্বপ্রস্তুতি (Prerequisites)
মাইগ্রেশন শুরু করার আগে নিচের জিনিসগুলো নিশ্চিত করুন:
1. **GitHub Repository:** আপনার কোডবেস অবশ্যই GitHub (বা অন্য কোনো Git host)-এ পুশ করা থাকতে হবে।
2. **Droplet Access:** আপনার Droplet-এ SSH করার জন্য SSH Key বা Password প্রস্তুত রাখুন।
3. **Domain Registrar Control:** আপনার ডোমেইনের (যেমন: `buykori.app`) DNS রেকর্ড পরিবর্তন করার অ্যাক্সেস থাকতে হবে।

---

## 🛠️ ধাপ ১: Droplet সম্পূর্ণ খালি করা (Wipe & Rebuild)

আপনার বর্তমান Droplet-এ WordPress ইন্সটল করা আছে। এটিকে একদম ফ্রেশ Ubuntu 24.04-এ রূপান্তর করতে নিচের পদক্ষেপগুলো অনুসরণ করুন:

1. **DigitalOcean Control Panel**-এ লগইন করুন।
2. আপনার Droplet **`wordpress-s-1vcpu-2gb-sgp1`** এ ক্লিক করুন।
3. উপরের ডানদিকের কোণায় **"Actions"** (নীল বাটন) ড্রপডাউনটি ওপেন করুন।
4. সেখানে **"Rebuild"** অপশনটি সিলেক্ট করুন।
5. **Image** হিসেবে **"Ubuntu 24.04 LTS x64"** (Standard Image) সিলেক্ট করুন।
6. **"Rebuild"** বাটনে ক্লিক করে কনফার্ম করুন।
7. কয়েক মিনিটের মধ্যে আপনার Droplet-টি রিবিল্ড হয়ে যাবে।
   
> [!NOTE]
   > **রিবিল্ড করার সুবিধা:** আপনার Droplet-এর IP অ্যাড্রেস (`159.223.59.78`) অপরিবর্তিত থাকবে, কিন্তু ভেতরের সব WordPress ফাইল এবং ডাটাবেস মুছে গিয়ে একটি একদম নতুন এবং ফ্রেশ ওএস (OS) লোড হবে।

---

## 💻 ধাপ ২: সার্ভারে কোড ক্লোন করা (SSH & Git Clone)

1. আপনার লোকাল কম্পিউটারের টার্মিনাল বা PowerShell থেকে Droplet-এ SSH-এর মাধ্যমে লগইন করুন:
   ```bash
   ssh root@159.223.59.78
   ```

2. সিস্টেম প্যাকেজগুলো আপডেট করুন এবং Git চেক করুন:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. প্রজেক্ট ডিরেক্টরি তৈরি করুন:
   ```bash
   sudo mkdir -p /var/www/buykori-adsync
   sudo chown -R ubuntu:ubuntu /var/www/buykori-adsync  # অথবা আপনার ইউজার
   ```

4. আপনার GitHub রিপোজিটরি থেকে কোডটি ক্লোন করুন:
   ```bash
   git clone <YOUR_GITHUB_REPO_URL> /var/www/buykori-adsync
   ```
   *(ব্যক্তিগত রিপোজিটরি হলে GitHub Username এবং Personal Access Token বা SSH Key ব্যবহার করতে হবে)*

---

## ⚡ ধাপ ৩: Auto-Setup স্ক্রিপ্ট রান করা

আমরা আপনার প্রজেক্টের ভেতরে `deploy/setup.sh` স্ক্রিপ্টটি তৈরি করে রেখেছি। এটি রান করলে সিস্টেমের সব ডিপেন্ডেন্সি (Python, Nginx, PostgreSQL, Supervisor) অটোমেটিক কনফিগার হয়ে যাবে।

1. স্ক্রিপ্ট ডিরেক্টরিতে যান:
   ```bash
   cd /var/www/buykori-adsync/deploy
   ```

2. স্ক্রিপ্টটিকে এক্সিকিউটেবল পারমিশন দিন এবং রান করুন:
   ```bash
   chmod +x setup.sh
   sudo ./setup.sh
   ```

3. রান করার পর স্ক্রিপ্টটি আপনাকে কিছু ইনপুট দিতে বলবে:
   - **Primary Domain:** আপনার ডোমেইনটি লিখুন (যেমন: `api.buykori.app` বা আপনার ট্র্যাকিং সাবডোমেইন)।
   - **Admin Username:** আপনার অ্যাডমিন প্যানেলের ইউজারনেম দিন (ডিফল্ট: `admin`)।
   - **Admin Password:** অ্যাডমিন পাসওয়ার্ড দিন (ফাঁকা রাখলে অটোমেটিক জেনারেট হবে)।
   - **Admin API Key:** অ্যাডমিন এপিআই কী দিন (ফাঁকা রাখলে অটোমেটিক জেনারেট হবে)।
   - **DNS Pointing check:** যদি আপনার ডোমেইনের DNS ইতিমধ্যে এই আইপিতে পয়েন্ট করা থাকে, তবে `y` চাপুন। স্ক্রিপ্টটি অটোমেটিক Let's Encrypt SSL সেটাপ করে নেবে। অন্যথায় `n` চাপুন (পরে কীভাবে সেটআপ করবেন তা নিচে বলা হয়েছে)।

4. স্ক্রিপ্ট শেষ হওয়ার পর স্ক্রিনে জেনারেট হওয়া পাসওয়ার্ড ও ক্রেডেনশিয়ালগুলো স্ক্রিনশট নিয়ে বা কপি করে সুরক্ষিত জায়গায় সেভ করুন।

---

## 🗄️ ধাপ ৪: ডাটাবেস মাইগ্রেশন (Heroku থেকে DO-তে ডাটা ট্রান্সফার)

Heroku PostgreSQL থেকে আপনার সমস্ত ক্লায়েন্ট ও ইভেন্টের ডাটা নতুন DigitalOcean PostgreSQL-এ ট্রান্সফার করতে নিচের কমান্ডগুলো ব্যবহার করুন।

### ৪.১. Heroku DB Connection URI খুঁজে বের করা
আপনার লোকাল পিসি থেকে বা Heroku CLI থেকে Heroku ডাটাবেসের URI সংগ্রহ করুন:
```bash
heroku config:get DATABASE_URL -a <YOUR_HEROKU_APP_NAME>
```
এটি দেখতে এমন হবে: `postgres://<user>:<password>@<host>:<port>/<dbname>`

### ৪.২. Heroku থেকে ডাটা ডাম্প (pg_dump) নেওয়া
আপনার লোকাল কম্পিউটার থেকে নিচের কমান্ডটি রান করে ডাটাবেসের একটি ব্যাকআপ ফাইল তৈরি করুন:
```bash
pg_dump --no-owner --no-privileges --clean -d "<YOUR_HEROKU_DATABASE_URL>" -F c -f buykori_backup.dump
```

### ৪.৩. ব্যাকআপ ফাইলটি DigitalOcean সার্ভারে ট্রান্সফার করা (SCP)
লোকাল পিসি থেকে `scp` কমান্ডের মাধ্যমে ফাইলটি ড্রপলেটে পাঠান:
```bash
scp buykori_backup.dump root@159.223.59.78:/tmp/
```

### ৪.৪. DigitalOcean ডাটাবেসে ডাটা রিস্টোর করা
ড্রপলেট টার্মিনালে (SSH) ফিরে যান এবং ফাইলটি রিস্টোর করুন:
```bash
# ডাটাবেস রিস্টোর করার কমান্ড (setup.sh এর মাধ্যমে জেনারেট হওয়া DB পাসওয়ার্ড ব্যবহার করুন)
PGPASSWORD="<YOUR_DO_DB_PASSWORD>" pg_restore --no-owner --no-privileges -h 127.0.0.1 -U buykori -d buykori_adsync -c /tmp/buykori_backup.dump
```
*(রিস্টোর করার সময় কিছু Warning আসতে পারে, এগুলো স্বাভাবিক। কোনো বড় লাল Error না আসলে ডাটা ঠিকঠাক চলে গেছে।)*

---

## 🌐 ধাপ ৫: DNS ও SSL কনফিগারেশন

1. আপনার ডোমেইন প্রোভাইডারের (Cloudflare, Namecheap, ইত্যাদি) ড্যাশবোর্ডে যান।
2. আপনার ট্র্যাকিং সাবডোমেইনের (যেমন: `api.buykori.app`) DNS রেকর্ডে পরিবর্তন করুন:
   - **Type:** `A`
   - **Name / Host:** `api` (অথবা আপনার সাবডোমেইন নাম)
   - **Value / Points to:** `159.223.59.78`
   - **TTL:** Auto/Custom (যেমন 2 Min বা 5 Min)
3. DNS আপডেট হতে কয়েক মিনিট সময় লাগতে পারে। আপডেট হওয়ার পর সার্ভারে গিয়ে Let's Encrypt SSL সার্টিফিকেট জেনারেট করুন:
   ```bash
   sudo certbot --nginx -d api.buykori.app
   ```
   *(সব প্রম্পটে ইতিবাচক উত্তর দিন। এটি আপনার Nginx কনফিগ ফাইলটিকে অটোমেটিক SSL যুক্ত করে রিলোড করে দেবে।)*

---

## 🔍 ধাপ ৬: সার্ভিস পরীক্ষা ও ভেরিফিকেশন (Verification)

সবকিছু ঠিকঠাক কাজ করছে কিনা তা দেখতে নিচের কমান্ডগুলো সার্ভারে রান করে চেক করুন:

1. **Supervisor স্ট্যাটাস চেক:**
   ```bash
   sudo supervisorctl status
   ```
   আউটপুটে `buykori-web` এবং `buykori-worker` উভয় প্রসেসকেই `RUNNING` দেখাতে হবে।

2. **লাইভ লগ দেখা:**
   - ওয়েব সার্ভারের লগ: `tail -f /var/log/supervisor/buykori-web.err.log`
   - ব্যাকগ্রাউন্ড ওয়ার্কারের লগ: `tail -f /var/log/supervisor/buykori-worker.out.log`

3. **ব্রাউজারে ভেরিফিকেশন:**
   - Health Check URL ভিজিট করুন: `https://api.buykori.app/`
   - Detailed Health: `https://api.buykori.app/api/v1/health/detailed` (অ্যাডমিন লগইন লাগবে)
   - Admin Panel চেক করুন আপনার নতুন পাসওয়ার্ড দিয়ে লগইন করে।

---

## 🔄 ভবিষ্যৎ ডিপ্লয়মেন্ট (Future Updates)
পরবর্তীতে কোডে কোনো পরিবর্তন আনলে বা আমরা নতুন কোনো ফিচার যোগ করার পর আপনার সার্ভারে আপডেট দিতে ড্রপলেটের SSH-এ ঢুকে শুধু এই কমান্ডটি রান করবেন:
```bash
cd /var/www/buykori-adsync
sudo ./deploy/deploy.sh
```
এটি নিজে থেকেই কোড পুল করবে, ডিপেন্ডেন্সি আপডেট করবে, ডাটাবেস মাইগ্রেশন রান করবে এবং অ্যাপ্লিকেশন রিস্টার্ট করে দেবে! 🥳
