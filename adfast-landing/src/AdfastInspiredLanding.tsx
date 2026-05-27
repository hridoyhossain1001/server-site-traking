import { useState } from 'react';
import {
  Activity,
  ArrowRight,
  BarChart3,
  Check,
  ChevronDown,
  DatabaseZap,
  LineChart,
  Play,
  ShieldCheck,
  Sparkles,
  Target,
  type LucideIcon,
} from 'lucide-react';

const features: Array<[string, string, LucideIcon]> = [
  ['Track Real Engagement', 'Capture PageView, ViewContent, AddToCart, checkout intent and purchases with cleaner attribution.', BarChart3],
  ['Signal Health Doctor', 'Find missing product IDs, weak match quality and platform delivery warnings before campaigns waste budget.', ShieldCheck],
  ['Campaign Monitoring', 'See Meta, TikTok and GA4 event delivery status from one lightweight dashboard.', Activity],
];

const plans = [
  ['Free Plan', '$0', 'For testing one WooCommerce store', ['One store setup', 'Basic server events', 'Campaign URL builder']],
  ['Pro Plan', '$19', 'For growing stores and marketers', ['Meta, TikTok and GA4', 'Signal Health Doctor', 'Deferred Purchase control', 'Priority support']],
  ['Enterprise Plan', 'Custom', 'For agencies and multi-store teams', ['Multi-client dashboard', 'Custom domains', 'Advanced event quality']],
];

const faqs = [
  ['What is Buykori AdSync?', 'A server-side tracking platform that sends cleaner WooCommerce events to Meta CAPI, TikTok Events API and GA4.'],
  ['Does it support one-page landing pages?', 'Yes. One-page mode can wait for real checkout intent before sending InitiateCheckout.'],
  ['Can I use only TikTok or only Meta?', 'Yes. Platform toggles can control which destination receives events.'],
  ['What improves event match quality?', 'Content IDs, value, currency, click IDs, user agent, IP and hashed customer fields.'],
];

const CLIENT_PORTAL_URL = 'https://client.buykori.app';
const PRIVACY_URL = 'https://buykori.app/privacy';

function Logo() {
  return (
    <div className="bk-logo">
      <span><DatabaseZap size={15} /></span>
      <strong>Buykori AdSync</strong>
    </div>
  );
}

function DashboardPreview() {
  return (
    <div className="bk-dashboard">
      <div className="bk-window">
        <div className="bk-window-top"><i /><i /><i /><b /></div>
        <div className="bk-window-body">
          <aside>
            <Logo />
            {['Dashboard', 'Events', 'Quality', 'Reports', 'Settings'].map((item, index) => (
              <p className={index === 0 ? 'active' : ''} key={item}>{item}</p>
            ))}
          </aside>
          <main>
            <div className="bk-dash-head">
              <div>
                <small>Overview</small>
                <h3>Campaign dashboard</h3>
              </div>
              <span>Last 24h</span>
            </div>
            <div className="bk-metrics">
              {[
                ['Events', '16,928', '+12.6%'],
                ['Match Rate', '92.7%', '+6.3%'],
                ['Revenue', '$8.7K', '+18.1%'],
              ].map(([label, value, trend]) => (
                <article key={label}>
                  <small>{label}</small>
                  <strong>{value}</strong>
                  <em>{trend}</em>
                </article>
              ))}
            </div>
            <div className="bk-bars">
              {[38, 56, 42, 76, 68, 92, 64, 84, 58, 74].map((height, index) => (
                <span key={index} style={{ height: `${height}%` }} />
              ))}
            </div>
            <div className="bk-mini">
              <article>
                <div className="bk-ring">94</div>
                <div><b>Signal Health</b><p>Excellent event quality</p></div>
              </article>
              <article>
                <b>Top Events</b>
                <p><span>PageView</span><strong>9,842</strong></p>
                <p><span>ViewContent</span><strong>6,215</strong></p>
                <p><span>Purchase</span><strong>1,010</strong></p>
              </article>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

export default function AdfastInspiredLanding() {
  const [openFaq, setOpenFaq] = useState(0);

  return (
    <div className="bk-page">
      <div className="bk-canvas">
        <section className="bk-hero">
          <header className="bk-nav">
            <Logo />
            <nav>
              <a href="#features">Home</a>
              <a href="#product">Product</a>
              <a href="#solution">Solution</a>
              <a href="#pricing">Pricing</a>
              <a href="#faq">FAQ</a>
            </nav>
            <div><a href={CLIENT_PORTAL_URL}>Sign in</a><a className="bk-dark" href={CLIENT_PORTAL_URL}>Sign up</a></div>
          </header>

          <div className="bk-hero-grid">
            <div>
              <p className="bk-eyebrow">New update <span>|</span> Better server events for paid ads</p>
              <h1>Optimize Your <mark>Ad</mark> Tracking with Real-Time Data</h1>
              <p className="bk-sub">Monitor server-side event quality in real time, analyze campaign attribution, and send cleaner WooCommerce signals to Meta, TikTok and GA4.</p>
              <div className="bk-actions">
                <a className="bk-orange" href="#pricing">Get Started <ArrowRight size={15} /></a>
                <a className="bk-soft" href="#features"><Play size={15} /> How it Works</a>
              </div>
            </div>
            <DashboardPreview />
          </div>
        </section>

        <section className="bk-intro">
          <p>Buykori AdSync is an ads tracking dashboard platform designed to effectively optimize and monitor your advertising campaigns.</p>
        </section>

        <section id="features" className="bk-section">
          <div className="bk-section-head">
            <div><p className="bk-kicker">Key features</p><h2>Powerful Ads Management Features</h2></div>
            <div className="bk-tabs"><span>Tracking</span><span>Dashboard</span><span>Ad Spend</span><span>Customisable</span></div>
          </div>
          <div className="bk-feature-grid">
            {features.map(([title, body, Icon]) => (
              <article key={title as string}>
                <i><Icon size={20} /></i>
                <h3>{title}</h3>
                <p>{body}</p>
                <div><strong>{title === 'Signal Health Doctor' ? '94/100' : '+24.8%'}</strong><LineChart size={86} /></div>
              </article>
            ))}
          </div>
        </section>

        <section id="solution" className="bk-budget">
          <p className="bk-kicker">Budgeting for ads</p>
          <h2>Manage and Optimize the Advertising Budget for Maximum Results.</h2>
          <div className="bk-table">
            <h3>Ad Spend</h3>
            <table>
              <thead><tr><th>Platform</th><th>Campaign Name</th><th>Clicks</th><th>Impressions</th></tr></thead>
              <tbody>
                {[
                  ['Meta', 't-shirt_launch_may', '7,148', '92.4K'],
                  ['TikTok', 'summer_offer_cod', '4,502', '61.8K'],
                  ['GA4', 'brand_search_bd', '2,187', '28.9K'],
                  ['Direct', 'retargeting_flow', '1,044', '13.2K'],
                ].map((row) => <tr key={row[1]}>{row.map((cell) => <td key={cell}>{cell}</td>)}</tr>)}
              </tbody>
            </table>
          </div>
          <div className="bk-budget-notes">
            {['Real-Time Tracking', 'Budget Adjustment', 'Cost Per Conversion'].map((item) => (
              <article key={item}><Target size={18} /><h3>{item}</h3><p>Use clear event data before scaling campaign budget.</p></article>
            ))}
          </div>
        </section>

        <section className="bk-integrations">
          <p className="bk-kicker">Integrations</p>
          <h2>Easy Integration with Your Advertising Platform</h2>
          <p>Connect AdSync with your advertising platforms and tools from one connected workflow.</p>
          <div>{['Meta CAPI', 'TikTok', 'GA4', 'WooCommerce', 'Google Ads', 'LinkedIn', 'Pinterest'].map((item) => <span key={item}>{item}</span>)}</div>
        </section>

        <section id="pricing" className="bk-pricing">
          <p className="bk-kicker">Pricing</p>
          <h2>Price is Just a Number, Focus on the Benefits</h2>
          <div className="bk-plan-grid">
            {plans.map(([name, price, note, points], index) => (
              <article className={index === 1 ? 'featured' : ''} key={name as string}>
                <h3>{name}</h3>
                <strong>{price}<span>{price !== 'Custom' ? '/month' : ''}</span></strong>
                <p>{note}</p>
                <a href={CLIENT_PORTAL_URL}>{index === 1 ? 'Start 14 Days Trial' : index === 2 ? 'Talk to sales' : 'Start for free'}</a>
                <ul>{(points as string[]).map((point) => <li key={point}><Check size={15} />{point}</li>)}</ul>
              </article>
            ))}
          </div>
        </section>

        <section id="faq" className="bk-faq">
          <div><p className="bk-kicker">FAQ</p><h2>Got questions about Buykori? We've got answers.</h2><p>Simple answers for campaign tracking, one-page landing pages and event quality.</p></div>
          <div className="bk-faq-list">
            {faqs.map(([question, answer], index) => (
              <article className={openFaq === index ? 'open' : ''} key={question}>
                <button onClick={() => setOpenFaq(openFaq === index ? -1 : index)}>{question}<ChevronDown size={17} /></button>
                <p>{answer}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="bk-cta">
          <h2>Ready to Optimize Your Ads and Maximize Your Results?</h2>
          <p>Start using Buykori AdSync today and take control of your ad campaigns with real-time insights.</p>
          <a href={CLIENT_PORTAL_URL}>Get Started for Free <ArrowRight size={15} /></a>
        </section>

        <footer className="bk-footer">
          <Logo />
          <div><Sparkles size={16} /> Meta <span>TikTok</span><span>GA4</span></div>
          <a href={PRIVACY_URL}>Privacy Policy</a>
        </footer>
      </div>
    </div>
  );
}
