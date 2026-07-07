import { useState, useRef, useEffect } from "react";
import {
  Star, ShoppingCart, Truck, MessageSquare, Store, Bike,
  CreditCard, Shield, MapPin, Package, Clock, CheckCircle,
  DollarSign, Eye, ChevronRight, ArrowLeft, Plus, Minus,
  Search, TrendingUp, BarChart2, X, Bell, Settings, Check,
  Wallet, Users, Home, Zap, Award, QrCode, ChevronDown, Menu,
  Send, Phone, MoreVertical, Circle
} from "lucide-react";

// ─── Brand ───────────────────────────────────────────────────────────────────

function DeliLogo({ dark = false }: { dark?: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <img
        src="/deli-logo.png"
        alt="Deli logo"
        className="h-9 w-auto object-contain"
      />
      <span
        className="font-black text-[22px] tracking-[-0.03em]"
        style={{ fontFamily: "'Bricolage Grotesque', sans-serif", color: dark ? "#F0EDE8" : "#0A0A0A" }}
      >
        deli
      </span>
    </div>
  );
}

// ─── Data ────────────────────────────────────────────────────────────────────

const RESTAURANTS = [
  { id: 1, name: "Mama Nkechi's Kitchen", cuisine: "Nigerian · Soups · Swallows", rating: 4.8, time: "25–35 min", fee: "₦500", image: "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&h=260&fit=crop&auto=format", open: true, tag: "Popular" },
  { id: 2, name: "Lagos Grill House", cuisine: "BBQ · Suya · Grills", rating: 4.6, time: "30–45 min", fee: "₦600", image: "https://images.unsplash.com/photo-1544025162-d76538729428?w=400&h=260&fit=crop&auto=format", open: true, tag: "Top Rated" },
  { id: 3, name: "Iya Basira Spot", cuisine: "Amala · Ewedu · Gbegiri", rating: 4.9, time: "20–30 min", fee: "₦400", image: "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&h=260&fit=crop&auto=format", open: true, tag: "Fan Fave" },
  { id: 4, name: "Mr. Burger Lagos", cuisine: "Burgers · Fries · Wraps", rating: 4.4, time: "20–30 min", fee: "₦500", image: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=260&fit=crop&auto=format", open: false, tag: null },
];

const MENU_ITEMS: Record<number, MenuItem[]> = {
  1: [
    { id: 1, name: "Jollof Rice + Chicken", price: 2500, rating: 4.9, desc: "Smoky party jollof with grilled chicken, coleslaw & plantain.", image: "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400&h=300&fit=crop&auto=format", popular: true },
    { id: 2, name: "Egusi Soup + Eba", price: 3200, rating: 4.8, desc: "Rich egusi with assorted meat and stockfish, served with smooth eba.", image: "https://images.unsplash.com/photo-1547592180-85f173990554?w=400&h=300&fit=crop&auto=format", popular: true },
    { id: 3, name: "Pepper Soup (Catfish)", price: 3800, rating: 4.7, desc: "Hot and spicy catfish pepper soup with fresh herbs.", image: "https://images.unsplash.com/photo-1547592180-85f173990554?w=400&h=300&fit=crop&auto=format", popular: false },
    { id: 4, name: "Fried Rice + Turkey", price: 2800, rating: 4.6, desc: "Nigerian-style fried rice with mixed vegetables and turkey leg.", image: "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400&h=300&fit=crop&auto=format", popular: false },
  ],
  2: [
    { id: 5, name: "Suya Platter (500g)", price: 4500, rating: 4.9, desc: "Spiced beef suya with sliced onions, tomatoes, and yaji.", image: "https://images.unsplash.com/photo-1544025162-d76538729428?w=400&h=300&fit=crop&auto=format", popular: true },
    { id: 6, name: "BBQ Chicken (Half)", price: 5500, rating: 4.7, desc: "Smoky half chicken with house BBQ glaze, coleslaw and chips.", image: "https://images.unsplash.com/photo-1562967914-608f82629710?w=400&h=300&fit=crop&auto=format", popular: true },
    { id: 7, name: "Grilled Fish + Rice", price: 6000, rating: 4.8, desc: "Fresh tilapia grilled with pepper and herbs. Served with white rice.", image: "https://images.unsplash.com/photo-1544025162-d76538729428?w=400&h=300&fit=crop&auto=format", popular: false },
  ],
  3: [
    { id: 8, name: "Amala + Ewedu + Gbegiri", price: 1800, rating: 5.0, desc: "Smooth amala with silky ewedu, gbegiri, and assorted meat stew.", image: "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&h=300&fit=crop&auto=format", popular: true },
    { id: 9, name: "Pounded Yam + Egusi", price: 2200, rating: 4.9, desc: "Soft pounded yam with egusi soup and assorted proteins.", image: "https://images.unsplash.com/photo-1547592180-85f173990554?w=400&h=300&fit=crop&auto=format", popular: true },
  ],
  4: [
    { id: 10, name: "Classic Beef Burger", price: 2200, rating: 4.5, desc: "Juicy beef patty with lettuce, tomato, cheese, and special sauce.", image: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop&auto=format", popular: true },
    { id: 11, name: "Chicken Shawarma", price: 1800, rating: 4.4, desc: "Spiced chicken strips with cabbage, carrots, and garlic sauce.", image: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop&auto=format", popular: false },
  ],
};

interface MenuItem { id: number; name: string; price: number; rating: number; desc: string; image: string; popular: boolean; }

const CUSTOMER_STEPS = [
  { num: "01", title: "Say Hey 👋", desc: "Open Deli on WhatsApp and send a message. No app download needed — just tap and go.", icon: MessageSquare },
  { num: "02", title: "Browse or Type", desc: "Pick 'Browse Restaurants' or type your craving and let Deli find it for you instantly.", icon: Search },
  { num: "03", title: "Pick Your Meal", desc: "Select your restaurant, browse the menu card, and add favourites to your cart.", icon: ShoppingCart },
  { num: "04", title: "Pay with Nomba", desc: "Confirm your order and pay securely via Nomba. Safe, instant, and card-not-stored.", icon: CreditCard },
  { num: "05", title: "Track Delivery", desc: "Your rider gets notified instantly. Follow order status right in WhatsApp.", icon: Truck },
  { num: "06", title: "Eat & Review", desc: "Enjoy your meal and drop a quick rating. Your feedback shapes the next experience.", icon: Star },
];

const RESTAURANT_FEATURES = [
  { title: "Quick Registration", desc: "Sign up as a partner in minutes. Share your menu or photos directly in WhatsApp — no portal required.", icon: Store },
  { title: "Upload Products", desc: "Add menu items with photos, descriptions, and prices. Organised by category for easy customer browsing.", icon: Package },
  { title: "Live Availability", desc: "Toggle your restaurant open or closed anytime. Adjust item availability and prep time on the fly.", icon: Eye },
  { title: "Accept or Reject", desc: "Get order notifications and accept or reject with one tap. Send custom prep time updates.", icon: Check },
  { title: "Manage Hours", desc: "Set daily opening and closing times per weekday. Holiday mode and snooze included.", icon: Clock },
  { title: "Weekly Payouts", desc: "Revenue tracked per order. Payouts processed weekly via Nomba direct to your bank account.", icon: DollarSign },
];

const RIDER_FEATURES = [
  { title: "Easy Sign-Up", desc: "Register in minutes — send your name, phone, and vehicle type via WhatsApp and get approved.", icon: Bike },
  { title: "Set Availability", desc: "Mark yourself available or unavailable anytime. No minimum hours, no penalties.", icon: Circle },
  { title: "Custom Pricing", desc: "Set your per-km rate and base delivery fee. You control what you earn.", icon: DollarSign },
  { title: "View Pending Jobs", desc: "See nearby delivery requests with pickup, drop address, and payout before accepting.", icon: MapPin },
  { title: "Confirm Pickup", desc: "Notify the restaurant and customer when you collect. Status updates automatically.", icon: Package },
  { title: "Instant Earnings", desc: "Mark delivery complete when the customer receives. Earnings credited to your wallet instantly.", icon: CheckCircle },
];

// ─── WhatsApp Types ───────────────────────────────────────────────────────────

type WAScreen =
  | "welcome" | "customer_home" | "browse_restaurants" | "restaurant_menu"
  | "item_detail" | "cart" | "delivery_details" | "rider_choice"
  | "payment" | "order_success" | "tracking" | "review" | "review_done"
  | "restaurant_home" | "rider_home";

interface WAMsg { side: "bot" | "user"; text: string; }

// ─── Top Nav ─────────────────────────────────────────────────────────────────

function TopNav({
  onCtaClick,
  onScrollTo,
  onAdminClick,
}: {
  onCtaClick: () => void;
  onScrollTo: (id: string) => void;
  onAdminClick: () => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-100" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <DeliLogo dark={false} />
        <div className="hidden md:flex items-center gap-8">
          {[["How it Works", "how-it-works"], ["For Restaurants", "restaurants"], ["For Riders", "riders"], ["Try Live", "whatsapp"]].map(([label, id]) => (
            <button key={id} onClick={() => onScrollTo(id)} className="text-sm font-medium text-gray-600 hover:text-[#0A0A0A] transition-colors">
              {label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <button onClick={onAdminClick} className="hidden md:block text-sm font-semibold text-[#0A0A0A] hover:text-[#E01E37] transition-colors">
            Partner Login
          </button>
          <button
            onClick={onCtaClick}
            className="px-5 py-2.5 rounded-full text-sm font-bold text-white transition-all hover:scale-105 active:scale-95"
            style={{ background: "linear-gradient(135deg, #E01E37 0%, #C01530 100%)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            Start Ordering
          </button>
          <button className="md:hidden p-2" onClick={() => setMenuOpen(!menuOpen)}>
            <Menu size={20} className="text-gray-700" />
          </button>
        </div>
      </div>
      {menuOpen && (
        <div className="md:hidden bg-white border-t border-gray-100 px-6 py-4 flex flex-col gap-4">
          {[["How it Works", "how-it-works"], ["For Restaurants", "restaurants"], ["For Riders", "riders"], ["Try Live", "whatsapp"]].map(([label, id]) => (
            <button key={id} onClick={() => { onScrollTo(id); setMenuOpen(false); }} className="text-sm font-medium text-gray-700 text-left">
              {label}
            </button>
          ))}
          <button onClick={() => { onAdminClick(); setMenuOpen(false); }} className="text-sm font-semibold text-[#E01E37] text-left">
            Partner Login
          </button>
        </div>
      )}
    </nav>
  );
}

// ─── Hero Section ─────────────────────────────────────────────────────────────

function HeroSection({ onCta, onScrollTo }: { onCta: () => void; onScrollTo: (id: string) => void }) {
  return (
    <section className="min-h-screen pt-16 flex items-center overflow-hidden" style={{ background: "#0A0A0A" }}>
      <div className="max-w-6xl mx-auto px-6 py-20 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left */}
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full mb-6 border border-white/10 bg-white/5">
              <div className="w-2 h-2 rounded-full bg-[#25D366]" />
              <span className="text-xs font-semibold text-white/60 tracking-widest uppercase" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                WhatsApp-first ordering
              </span>
            </div>
            <h1
              className="font-black text-white leading-[1.05] tracking-[-0.03em] mb-6"
              style={{ fontFamily: "'Bricolage Grotesque', sans-serif", fontSize: "clamp(2.8rem, 5vw, 4.5rem)" }}
            >
              Your next meal is<br />
              <span style={{ color: "#E01E37" }}>one message</span><br />
              away.
            </h1>
            <p className="text-white/60 text-lg leading-relaxed mb-8 max-w-md" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Order food, manage your restaurant, or deliver in Lagos — all inside WhatsApp. No app download. No friction. Just food.
            </p>
            <div className="flex flex-wrap gap-4">
              <button
                onClick={onCta}
                className="flex items-center gap-2.5 px-7 py-4 rounded-full font-bold text-white text-base transition-all hover:scale-105 active:scale-95"
                style={{ background: "linear-gradient(135deg, #E01E37 0%, #C01530 100%)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z" /></svg>
                Start ordering
              </button>
              <button
                onClick={() => onScrollTo("how-it-works")}
                className="flex items-center gap-2 px-7 py-4 rounded-full font-semibold text-white/80 text-base border border-white/15 hover:border-white/30 hover:text-white transition-all"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                See how it works <ChevronRight size={16} />
              </button>
            </div>
            {/* Trust badges */}
            <div className="flex flex-wrap items-center gap-5 mt-10 pt-8 border-t border-white/10">
              {[["12k+", "Orders placed"], ["300+", "Restaurants"], ["98%", "On-time rate"]].map(([num, label]) => (
                <div key={label}>
                  <div className="text-2xl font-black text-white" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{num}</div>
                  <div className="text-xs text-white/40 mt-0.5" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{label}</div>
                </div>
              ))}
              <div className="h-10 w-px bg-white/10 hidden sm:block" />
              <div className="flex items-center gap-2">
                <Shield size={16} className="text-[#C9A84C]" />
                <span className="text-sm text-white/50" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Secured by <span className="text-[#C9A84C] font-semibold">Nomba</span></span>
              </div>
            </div>
          </div>

          {/* Right — Hero Composition */}
          <div className="relative hidden lg:block" style={{ height: "560px" }}>
            {/* Main food image */}
            <div className="absolute right-0 top-0 w-[380px] h-[440px] rounded-3xl overflow-hidden" style={{ background: "#1A1A1A" }}>
              <img src="https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=760&h=880&fit=crop&auto=format" alt="Delicious Nigerian food" className="w-full h-full object-cover" />
              <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(10,10,10,0.4) 0%, transparent 60%)" }} />
            </div>

            {/* WhatsApp chat bubble */}
            <div className="absolute left-0 top-16 w-[240px] rounded-2xl overflow-hidden shadow-2xl" style={{ background: "#111B21", border: "1px solid rgba(255,255,255,0.08)" }}>
              <div className="flex items-center gap-2 px-3 py-2.5" style={{ background: "#1F2C34" }}>
                <div className="w-7 h-7 rounded-full flex items-center justify-center bg-[#E01E37]">
                  <span className="text-white text-xs font-black" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>d</span>
                </div>
                <div>
                  <div className="text-white text-xs font-semibold" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Deli 🍽️</div>
                  <div className="text-[10px]" style={{ color: "#25D366" }}>online</div>
                </div>
              </div>
              <div className="p-3 space-y-2">
                <div className="rounded-lg rounded-tl-sm p-2.5 text-[11px] text-white/90 leading-relaxed" style={{ background: "#1F2C34", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                  👋 Welcome to <strong>Deli!</strong> What can I get for you today?
                </div>
                <div className="rounded-lg rounded-tr-sm p-2.5 text-[11px] text-white/90 ml-4" style={{ background: "#005C4B", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                  Browse restaurants 🍽️
                </div>
                <div className="rounded-lg rounded-tl-sm p-2.5 text-[11px] text-white/90 leading-relaxed" style={{ background: "#1F2C34", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                  🔥 <strong>Mama Nkechi&apos;s Kitchen</strong><br />Jollof Rice + Chicken — ₦2,500
                </div>
              </div>
            </div>

            {/* Nomba payment card */}
            <div className="absolute left-4 bottom-12 w-[220px] rounded-2xl p-4 shadow-2xl" style={{ background: "linear-gradient(135deg, #1A1A1A 0%, #252525 100%)", border: "1px solid rgba(201,168,76,0.2)" }}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-bold tracking-widest uppercase text-[#C9A84C]" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Nomba Pay</span>
                <Shield size={12} className="text-[#C9A84C]" />
              </div>
              <div className="text-white font-black text-2xl mb-1" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>₦3,700</div>
              <div className="text-white/40 text-[10px] mb-3" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>1× Jollof Rice + ₦500 delivery</div>
              <div className="w-full py-2 rounded-xl text-center text-[11px] font-bold text-white" style={{ background: "#E01E37", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                Pay Securely →
              </div>
            </div>

            {/* QR card */}
            <div className="absolute right-[-16px] bottom-0 w-[140px] rounded-2xl p-3 shadow-2xl" style={{ background: "#0F0F0F", border: "1px solid rgba(255,255,255,0.08)" }}>
              <div className="w-full aspect-square rounded-xl flex items-center justify-center mb-2" style={{ background: "#1A1A1A" }}>
                <QrCode size={56} className="text-white/60" />
              </div>
              <div className="text-center text-[10px] font-semibold text-white/40" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Scan to order</div>
              <div className="text-center text-[10px] font-black text-white/20 mt-0.5" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>deli.ng/start</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ─── Section Header ───────────────────────────────────────────────────────────

function SectionHeader({ tag, title, sub, light = false }: { tag: string; title: string; sub: string; light?: boolean }) {
  return (
    <div className="text-center mb-14">
      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full mb-4 border" style={{ borderColor: light ? "rgba(0,0,0,0.1)" : "rgba(255,255,255,0.1)", background: light ? "rgba(0,0,0,0.04)" : "rgba(255,255,255,0.04)" }}>
        <span className="text-xs font-bold tracking-widest uppercase" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", color: "#E01E37" }}>{tag}</span>
      </div>
      <h2 className="font-black tracking-tight leading-tight mb-4" style={{ fontFamily: "'Bricolage Grotesque', sans-serif", fontSize: "clamp(1.8rem, 3.5vw, 3rem)", color: light ? "#0A0A0A" : "#F0EDE8" }}>
        {title}
      </h2>
      <p className="max-w-xl mx-auto text-base leading-relaxed" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", color: light ? "#555" : "rgba(240,237,232,0.55)" }}>
        {sub}
      </p>
    </div>
  );
}

// ─── Customer Section ─────────────────────────────────────────────────────────

function CustomerSection() {
  return (
    <section id="how-it-works" className="py-24 px-6" style={{ background: "#0F0F0F" }}>
      <div className="max-w-6xl mx-auto">
        <SectionHeader
          tag="For Customers"
          title="Food ordering made ridiculously simple"
          sub="Six steps. Zero app downloads. Order from the comfort of your WhatsApp."
        />

        {/* Steps */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-20">
          {CUSTOMER_STEPS.map((step, i) => (
            <div key={step.num} className="rounded-2xl p-6 border relative overflow-hidden group hover:border-white/15 transition-colors" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
              <div className="absolute top-4 right-4 text-5xl font-black tracking-tighter opacity-[0.04] select-none" style={{ fontFamily: "'Bricolage Grotesque', sans-serif", color: "#F0EDE8" }}>
                {step.num}
              </div>
              <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style={{ background: i % 3 === 0 ? "rgba(224,30,55,0.12)" : i % 3 === 1 ? "rgba(201,168,76,0.12)" : "rgba(37,211,102,0.1)" }}>
                <step.icon size={18} style={{ color: i % 3 === 0 ? "#E01E37" : i % 3 === 1 ? "#C9A84C" : "#25D366" }} />
              </div>
              <h3 className="font-bold text-white mb-2 text-base" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{step.title}</h3>
              <p className="text-sm leading-relaxed text-white/50" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{step.desc}</p>
            </div>
          ))}
        </div>

        {/* Featured Meal Cards */}
        <div className="mb-6">
          <h3 className="font-black text-white text-xl mb-6" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>
            🔥 Popular right now
          </h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            { name: "Jollof Rice + Chicken", restaurant: "Mama Nkechi's", price: "₦2,500", rating: 4.9, time: "25 min", image: "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400&h=280&fit=crop&auto=format" },
            { name: "Suya Platter 500g", restaurant: "Lagos Grill House", price: "₦4,500", rating: 4.9, time: "35 min", image: "https://images.unsplash.com/photo-1544025162-d76538729428?w=400&h=280&fit=crop&auto=format" },
            { name: "Amala + Ewedu", restaurant: "Iya Basira Spot", price: "₦1,800", rating: 5.0, time: "22 min", image: "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&h=280&fit=crop&auto=format" },
            { name: "Classic Beef Burger", restaurant: "Mr. Burger Lagos", price: "₦2,200", rating: 4.5, time: "28 min", image: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=280&fit=crop&auto=format" },
          ].map((item) => (
            <div key={item.name} className="rounded-2xl overflow-hidden border hover:border-white/15 transition-all group cursor-pointer hover:-translate-y-1" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
              <div className="relative h-44 bg-[#1A1A1A] overflow-hidden">
                <img src={item.image} alt={item.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                <div className="absolute top-3 right-3 flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold" style={{ background: "rgba(10,10,10,0.7)", color: "#F0EDE8", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                  <Star size={10} fill="#C9A84C" stroke="none" />{item.rating}
                </div>
              </div>
              <div className="p-4">
                <div className="text-xs text-white/40 mb-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{item.restaurant}</div>
                <div className="font-bold text-white text-sm mb-3" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{item.name}</div>
                <div className="flex items-center justify-between">
                  <span className="font-black text-[#E01E37] text-base" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{item.price}</span>
                  <span className="text-xs text-white/30 flex items-center gap-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}><Clock size={11} />{item.time}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── Restaurant Section ───────────────────────────────────────────────────────

function RestaurantSection({ onCta }: { onCta: () => void }) {
  return (
    <section id="restaurants" className="py-24 px-6" style={{ background: "#0A0A0A" }}>
      <div className="max-w-6xl mx-auto">
        <SectionHeader
          tag="For Restaurants"
          title="Grow your restaurant with zero extra kit"
          sub="Register, list your menu, and start receiving orders — all managed from WhatsApp."
        />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-12">
          {RESTAURANT_FEATURES.map((f, i) => (
            <div key={f.title} className="rounded-2xl p-6 border" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
              <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style={{ background: "rgba(224,30,55,0.1)" }}>
                <f.icon size={18} className="text-[#E01E37]" />
              </div>
              <h3 className="font-bold text-white mb-2" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{f.title}</h3>
              <p className="text-sm text-white/50 leading-relaxed" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{f.desc}</p>
            </div>
          ))}
        </div>

        <div className="rounded-2xl p-8 flex flex-col sm:flex-row items-center justify-between gap-6" style={{ background: "linear-gradient(135deg, #1A0508 0%, #1A0A0A 100%)", border: "1px solid rgba(224,30,55,0.2)" }}>
          <div>
            <div className="text-sm font-semibold text-[#E01E37] mb-2" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Ready to serve more customers?</div>
            <div className="text-2xl font-black text-white" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>Register your restaurant today</div>
            <div className="text-white/50 text-sm mt-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Free to join. Commission only on orders received.</div>
          </div>
          <button onClick={onCta} className="shrink-0 px-8 py-4 rounded-full font-bold text-white text-base transition-all hover:scale-105 active:scale-95" style={{ background: "linear-gradient(135deg, #E01E37 0%, #C01530 100%)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
            Register Restaurant →
          </button>
        </div>
      </div>
    </section>
  );
}

// ─── Rider Section ───────────────────────────────────────────────────────────

function RiderSection({ onCta }: { onCta: () => void }) {
  return (
    <section id="riders" className="py-24 px-6" style={{ background: "#0F0F0F" }}>
      <div className="max-w-6xl mx-auto">
        <SectionHeader
          tag="For Riders"
          title="Earn on your own schedule"
          sub="Deliver food across Lagos with Deli. Set your own hours, rates, and vehicle type."
        />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-12">
          {RIDER_FEATURES.map((f) => (
            <div key={f.title} className="rounded-2xl p-6 border" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
              <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style={{ background: "rgba(201,168,76,0.1)" }}>
                <f.icon size={18} className="text-[#C9A84C]" />
              </div>
              <h3 className="font-bold text-white mb-2" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{f.title}</h3>
              <p className="text-sm text-white/50 leading-relaxed" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Earnings snapshot */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-12">
          {[["₦18,400", "Avg weekly earnings", TrendingUp, "#25D366"], ["47", "Deliveries this week", Bike, "#C9A84C"], ["4.9 ★", "Avg rider rating", Star, "#E01E37"]].map(([val, label, Icon, color]) => (
            <div key={label as string} className="rounded-2xl p-6 border text-center" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
              <Icon size={24} style={{ color, margin: "0 auto 12px" }} />
              <div className="text-3xl font-black text-white mb-1" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{val}</div>
              <div className="text-sm text-white/40" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{label}</div>
            </div>
          ))}
        </div>

        <div className="rounded-2xl p-8 flex flex-col sm:flex-row items-center justify-between gap-6" style={{ background: "linear-gradient(135deg, #0A120A 0%, #0A0A0A 100%)", border: "1px solid rgba(37,211,102,0.15)" }}>
          <div>
            <div className="text-sm font-semibold mb-2" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", color: "#25D366" }}>Join 200+ active riders on Deli</div>
            <div className="text-2xl font-black text-white" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>Become a delivery rider</div>
            <div className="text-white/50 text-sm mt-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Set your availability. Earn instantly per delivery.</div>
          </div>
          <button onClick={onCta} className="shrink-0 px-8 py-4 rounded-full font-bold text-white text-base transition-all hover:scale-105 active:scale-95" style={{ background: "linear-gradient(135deg, #25D366 0%, #128C4C 100%)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
            Register as Rider →
          </button>
        </div>
      </div>
    </section>
  );
}

// ─── Payment Section ──────────────────────────────────────────────────────────

function PaymentSection() {
  return (
    <section id="payment" className="py-24 px-6" style={{ background: "#0A0A0A" }}>
      <div className="max-w-6xl mx-auto">
        <SectionHeader
          tag="Payments"
          title="Safe, seamless checkout via Nomba"
          sub="Every transaction on Deli is processed through Nomba — Nigeria's trusted payment infrastructure."
        />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          {/* Payment card mock */}
          <div className="rounded-3xl p-8 border" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
            <div className="flex items-center justify-between mb-6">
              <div>
                <div className="text-xs font-bold tracking-widest uppercase text-[#C9A84C] mb-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Nomba Secure Checkout</div>
                <div className="text-white font-black text-xl" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>Order #DEL-8842</div>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full" style={{ background: "rgba(37,211,102,0.1)", border: "1px solid rgba(37,211,102,0.2)" }}>
                <div className="w-2 h-2 rounded-full bg-[#25D366]" />
                <span className="text-xs font-semibold text-[#25D366]" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Secured</span>
              </div>
            </div>

            {/* Item list */}
            <div className="space-y-3 mb-6">
              {[["Jollof Rice + Chicken ×1", "₦2,500"], ["Puff Puff ×2", "₦1,000"]].map(([item, price]) => (
                <div key={item} className="flex justify-between items-center py-2 border-b border-white/5">
                  <span className="text-sm text-white/70" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{item}</span>
                  <span className="text-sm font-semibold text-white" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{price}</span>
                </div>
              ))}
            </div>

            {/* Fee breakdown */}
            <div className="rounded-xl p-4 space-y-2 mb-6" style={{ background: "#1A1A1A" }}>
              {[["Subtotal", "₦3,500"], ["Delivery fee", "₦500"], ["Service fee", "₦75"]].map(([label, val]) => (
                <div key={label} className="flex justify-between text-sm">
                  <span className="text-white/40" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{label}</span>
                  <span className="text-white/70" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{val}</span>
                </div>
              ))}
              <div className="flex justify-between font-bold border-t border-white/10 pt-2 mt-2">
                <span className="text-white" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Total</span>
                <span className="text-[#E01E37] text-lg font-black" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>₦4,075</span>
              </div>
            </div>

            <button className="w-full py-4 rounded-2xl font-bold text-white text-base transition-all hover:scale-[1.02] active:scale-95" style={{ background: "linear-gradient(135deg, #E01E37 0%, #C01530 100%)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Pay ₦4,075 with Nomba
            </button>
          </div>

          {/* Trust signals */}
          <div className="space-y-5">
            {[
              { icon: Shield, title: "Bank-grade encryption", desc: "All payment data is encrypted end-to-end. Your card details are never stored by Deli.", color: "#C9A84C" },
              { icon: CreditCard, title: "Multiple payment methods", desc: "Pay via card, bank transfer, or USSD. Nomba supports every major Nigerian bank.", color: "#E01E37" },
              { icon: Zap, title: "Instant confirmation", desc: "Orders are confirmed in seconds. Restaurants are notified the moment your payment clears.", color: "#25D366" },
              { icon: Award, title: "Dispute protection", desc: "Something wrong? Contact Deli support in WhatsApp and we resolve disputes within 24 hours.", color: "#C9A84C" },
            ].map((item) => (
              <div key={item.title} className="flex gap-4 items-start p-5 rounded-2xl border" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
                <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" style={{ background: `${item.color}18` }}>
                  <item.icon size={18} style={{ color: item.color }} />
                </div>
                <div>
                  <div className="font-bold text-white mb-1" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{item.title}</div>
                  <div className="text-sm text-white/50 leading-relaxed" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// ─── WhatsApp Prototype ───────────────────────────────────────────────────────

const WA_GREEN = "#25D366";
const WA_DARK = "#111B21";
const WA_HEADER = "#1F2C34";
const WA_BOT_BUBBLE = "#1F2C34";
const WA_USER_BUBBLE = "#005C4B";

function WaMsg({ side, text }: { side: "bot" | "user"; text: string }) {
  const isBot = side === "bot";
  return (
    <div className={`flex ${isBot ? "justify-start" : "justify-end"} mb-1.5`}>
      <div
        className="max-w-[85%] rounded-lg px-3 py-2 text-[12px] text-white leading-relaxed"
        style={{
          background: isBot ? WA_BOT_BUBBLE : WA_USER_BUBBLE,
          borderRadius: isBot ? "2px 12px 12px 12px" : "12px 2px 12px 12px",
          fontFamily: "'Plus Jakarta Sans', sans-serif",
        }}
        dangerouslySetInnerHTML={{ __html: text.replace(/\*([^*]+)\*/g, "<strong>$1</strong>").replace(/\n/g, "<br/>") }}
      />
    </div>
  );
}

function WhatsAppPrototype() {
  const [screen, setScreen] = useState<WAScreen>("welcome");
  const [history, setHistory] = useState<WAMsg[]>([
    { side: "bot", text: "👋 Welcome to *Deli* — your WhatsApp food marketplace in Lagos!" },
    { side: "bot", text: "I can help you order food, register your restaurant, or sign up as a delivery rider.\n\nWhat brings you here today?" },
  ]);
  const [selectedResto, setSelectedResto] = useState<typeof RESTAURANTS[0] | null>(null);
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);
  const [cart, setCart] = useState<{ item: MenuItem; qty: number }[]>([]);
  const [review, setReview] = useState(0);
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [history, screen]);

  const go = (next: WAScreen, userMsg?: string, botMsgs?: WAMsg[]) => {
    const msgs: WAMsg[] = [];
    if (userMsg) msgs.push({ side: "user", text: userMsg });
    if (botMsgs) msgs.push(...botMsgs);
    setHistory(prev => [...prev, ...msgs]);
    setScreen(next);
  };

  const cartTotal = cart.reduce((s, c) => s + c.item.price * c.qty, 0);
  const cartItems = cart.reduce((s, c) => s + c.qty, 0);

  const renderScreen = () => {
    switch (screen) {
      case "welcome":
        return (
          <div className="space-y-2 p-3">
            {[
              { label: "🛒 Order food", next: "customer_home" as WAScreen, msg: "Order food" },
              { label: "🏪 Register my restaurant", next: "restaurant_home" as WAScreen, msg: "Register my restaurant" },
              { label: "🏍️ Become a delivery rider", next: "rider_home" as WAScreen, msg: "Become a delivery rider" },
            ].map(o => (
              <button key={o.label} onClick={() => go(o.next, o.msg, o.next === "customer_home" ? [
                { side: "bot", text: "Great! Welcome, *foodie* 🎉\n\nI'm your Deli assistant. What would you like to do?" }
              ] : o.next === "restaurant_home" ? [
                { side: "bot", text: "Excellent! Let's get your restaurant on Deli 🏪\n\nPlease send your:\n• Restaurant name\n• Location/area\n• Cuisine type\n• Business phone number\n\nWe'll review and activate your account within 2 hours." }
              ] : [
                { side: "bot", text: "Welcome, rider! 🏍️\n\nTo register, please share:\n• Full name\n• Phone number\n• Vehicle type (Bike/Car/Bicycle)\n• Area you'll cover in Lagos\n\nWe'll activate your account and send you a welcome kit." }
              ])}
                className="w-full text-left px-3 py-2.5 rounded-xl text-[11px] font-semibold text-white border transition-colors hover:opacity-80"
                style={{ background: "rgba(37,211,102,0.08)", borderColor: "rgba(37,211,102,0.2)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                {o.label}
              </button>
            ))}
          </div>
        );

      case "customer_home":
        return (
          <div className="space-y-2 p-3">
            <div className="text-[10px] text-white/30 text-center mb-2 uppercase tracking-widest" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Customer Menu</div>
            {[
              { label: "📝 Type Order", next: "browse_restaurants" as WAScreen, msg: "Type Order" },
              { label: "🍽️ Browse Restaurants", next: "browse_restaurants" as WAScreen, msg: "Browse Restaurants" },
              { label: "🔍 Search Food", next: "browse_restaurants" as WAScreen, msg: "Search Food" },
              { label: "📦 My Orders", next: "customer_home" as WAScreen, msg: "My Orders" },
              { label: "📍 Change Location", next: "customer_home" as WAScreen, msg: "Change Location" },
            ].map((o, i) => (
              <button key={o.label} onClick={() => go(o.next, o.msg, i <= 2 ? [{ side: "bot", text: "Here are the top restaurants in your area 📍 *Lagos Island*:" }] : i === 3 ? [{ side: "bot", text: "You have *no recent orders* yet. Start ordering to see your history here!" }] : [{ side: "bot", text: "📍 Your current location: *Lagos Island*\nSend your new area to update it." }])}
                className="w-full text-left px-3 py-2.5 rounded-xl text-[11px] font-semibold text-white border transition-colors hover:opacity-80"
                style={{ background: "rgba(37,211,102,0.06)", borderColor: "rgba(37,211,102,0.15)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                {o.label}
              </button>
            ))}
          </div>
        );

      case "browse_restaurants":
        return (
          <div className="p-3 space-y-2">
            <div className="text-[10px] text-white/30 text-center mb-2 uppercase tracking-widest">Select a Restaurant</div>
            {RESTAURANTS.map(r => (
              <button key={r.id} onClick={() => {
                setSelectedResto(r);
                go("restaurant_menu", r.name, [{ side: "bot", text: `You chose *${r.name}* 🍽️\n\n${r.cuisine}\n⭐ ${r.rating} · 🕐 ${r.time} · 🛵 ${r.fee}\n\nHere's the menu:` }]);
              }}
                className="w-full text-left px-3 py-2.5 rounded-xl border transition-colors hover:opacity-80"
                style={{ background: "#1F2C34", borderColor: "rgba(255,255,255,0.08)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-[12px] font-bold text-white">{r.name}</div>
                    <div className="text-[10px] text-white/40 mt-0.5">{r.cuisine}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] font-semibold text-[#25D366]">{r.open ? "Open" : "Closed"}</div>
                    <div className="text-[10px] text-white/40">⭐ {r.rating}</div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        );

      case "restaurant_menu":
        const items = selectedResto ? (MENU_ITEMS[selectedResto.id] || []) : [];
        return (
          <div className="p-3 space-y-2">
            <button onClick={() => go("browse_restaurants", "← Back")} className="flex items-center gap-1 text-[10px] text-[#25D366] mb-2" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              <ArrowLeft size={10} /> Back to restaurants
            </button>
            <div className="text-[10px] text-white/30 text-center mb-2 uppercase tracking-widest">Select an Item</div>
            {items.map(item => (
              <button key={item.id} onClick={() => {
                setSelectedItem(item);
                go("item_detail", item.name, [{ side: "bot", text: `*${item.name}*\n₦${item.price.toLocaleString()}\n\n${item.desc}\n\n⭐ ${item.rating} rating${item.popular ? " · 🔥 Popular" : ""}` }]);
              }}
                className="w-full text-left px-3 py-2.5 rounded-xl border transition-colors hover:opacity-80"
                style={{ background: "#1F2C34", borderColor: "rgba(255,255,255,0.08)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-[12px] font-bold text-white">{item.name}{item.popular ? " 🔥" : ""}</div>
                    <div className="text-[10px] text-white/40 mt-0.5">⭐ {item.rating}</div>
                  </div>
                  <div className="text-[#C9A84C] font-black text-[13px]" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>₦{item.price.toLocaleString()}</div>
                </div>
              </button>
            ))}
            {cart.length > 0 && (
              <button onClick={() => go("cart", "View Cart", [{ side: "bot", text: `🛒 Your cart has *${cartItems} item(s)*.\nTotal: *₦${cartTotal.toLocaleString()}*\n\nReady to checkout?` }])}
                className="w-full py-2.5 rounded-xl font-bold text-white text-[11px] mt-2"
                style={{ background: "#E01E37", fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                View Cart ({cartItems}) · ₦{cartTotal.toLocaleString()}
              </button>
            )}
          </div>
        );

      case "item_detail":
        if (!selectedItem) return null;
        return (
          <div className="p-3 space-y-2">
            <div className="rounded-xl overflow-hidden h-32 bg-[#1A2328]">
              <img src={selectedItem.image} alt={selectedItem.name} className="w-full h-full object-cover" />
            </div>
            <button onClick={() => {
              setCart(prev => {
                const ex = prev.find(c => c.item.id === selectedItem.id);
                return ex ? prev.map(c => c.item.id === selectedItem.id ? { ...c, qty: c.qty + 1 } : c) : [...prev, { item: selectedItem, qty: 1 }];
              });
              go("restaurant_menu", "Add to Cart ✅", [{ side: "bot", text: `✅ *${selectedItem.name}* added to your cart!\n\nContinue browsing or checkout when ready.` }]);
            }}
              className="w-full py-2.5 rounded-xl font-bold text-white text-[11px]"
              style={{ background: "#E01E37", fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              Add to Cart — ₦{selectedItem.price.toLocaleString()}
            </button>
            <button onClick={() => go("restaurant_menu", "← Back to Menu")}
              className="w-full py-2 rounded-xl text-[11px] text-white/60 border border-white/10"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Back to Menu
            </button>
          </div>
        );

      case "cart":
        return (
          <div className="p-3 space-y-2">
            <div className="text-[10px] text-white/30 text-center mb-1 uppercase tracking-widest">Your Cart</div>
            {cart.map(c => (
              <div key={c.item.id} className="flex items-center justify-between px-3 py-2 rounded-xl border" style={{ background: "#1F2C34", borderColor: "rgba(255,255,255,0.08)" }}>
                <span className="text-[11px] text-white" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{c.item.name} ×{c.qty}</span>
                <span className="text-[11px] font-bold text-[#C9A84C]" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>₦{(c.item.price * c.qty).toLocaleString()}</span>
              </div>
            ))}
            <div className="flex justify-between px-3 py-2 border-t border-white/10 mt-1">
              <span className="text-[11px] text-white/50" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Total</span>
              <span className="text-[13px] font-black text-[#E01E37]" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>₦{cartTotal.toLocaleString()}</span>
            </div>
            <button onClick={() => go("delivery_details", "Checkout", [{ side: "bot", text: "📍 Confirm your delivery details:\n\n*Address:* 14 Karimu Kotun St, V.I.\n*Phone:* +234 801 234 5678\n\nIs this correct?" }])}
              className="w-full py-2.5 rounded-xl font-bold text-white text-[11px]"
              style={{ background: "#E01E37", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Proceed to Checkout →
            </button>
            <button onClick={() => go("restaurant_menu", "← Continue Shopping")}
              className="w-full py-2 rounded-xl text-[11px] text-white/60 border border-white/10"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Continue Shopping
            </button>
          </div>
        );

      case "delivery_details":
        return (
          <div className="p-3 space-y-2">
            <div className="rounded-xl p-3 border space-y-1.5" style={{ background: "#1F2C34", borderColor: "rgba(255,255,255,0.08)" }}>
              {[["📍 Address", "14 Karimu Kotun St, V.I."], ["📞 Phone", "+234 801 234 5678"], ["🛵 Delivery fee", "₦500"], ["⏱️ Est. time", "25–35 min"]].map(([k, v]) => (
                <div key={k as string} className="flex justify-between">
                  <span className="text-[10px] text-white/40" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{k}</span>
                  <span className="text-[10px] font-semibold text-white" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{v}</span>
                </div>
              ))}
            </div>
            <button onClick={() => go("payment", "Continue ✅", [{ side: "bot", text: "💳 Almost there!\n\nHere's your order summary:\n• Items: ₦" + cartTotal.toLocaleString() + "\n• Delivery: ₦500\n• Service fee: ₦75\n\n*Total: ₦" + (cartTotal + 575).toLocaleString() + "*\n\nPay securely with Nomba 👇" }])}
              className="w-full py-2.5 rounded-xl font-bold text-white text-[11px]"
              style={{ background: "#E01E37", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Continue ✅
            </button>
            <button onClick={() => go("cart", "← Go Back")}
              className="w-full py-2 rounded-xl text-[11px] text-white/60 border border-white/10"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Go Back
            </button>
          </div>
        );

      case "payment":
        return (
          <div className="p-3 space-y-2">
            <div className="rounded-xl p-3 border text-center" style={{ background: "linear-gradient(135deg, #1A0508, #1A1A1A)", borderColor: "rgba(224,30,55,0.2)" }}>
              <div className="text-[10px] font-bold text-[#C9A84C] mb-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Nomba Secure Payment</div>
              <div className="text-2xl font-black text-white mb-1" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>₦{(cartTotal + 575).toLocaleString()}</div>
              <div className="text-[10px] text-white/40" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Order #DEL-{Math.floor(8000 + Math.random() * 1000)}</div>
            </div>
            <button onClick={() => {
              setCart([]);
              go("order_success", "Pay Now 💳", [{ side: "bot", text: "✅ *Payment successful!*\n\nYour order has been placed and the restaurant has been notified.\n\n🏍️ A rider will be assigned shortly. You'll receive live updates here." }]);
            }}
              className="w-full py-2.5 rounded-xl font-bold text-white text-[11px]"
              style={{ background: "#E01E37", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Pay Now with Nomba 💳
            </button>
            <button onClick={() => go("delivery_details", "← Go Back")}
              className="w-full py-2 rounded-xl text-[11px] text-white/60 border border-white/10"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Go Back
            </button>
          </div>
        );

      case "order_success":
        return (
          <div className="p-4 text-center space-y-3">
            <div className="w-14 h-14 rounded-full flex items-center justify-center mx-auto" style={{ background: "rgba(37,211,102,0.15)" }}>
              <CheckCircle size={28} className="text-[#25D366]" />
            </div>
            <div className="text-white font-black text-base" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>Order Confirmed!</div>
            <div className="text-[11px] text-white/50" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Rider assigned — Emeka O. is on the way 🏍️</div>
            <button onClick={() => go("tracking", "Track Delivery", [{ side: "bot", text: "📍 *Live tracking*\n\n🏪 Restaurant: Preparing your order...\n🏍️ Rider: Emeka O. · 4.9 ⭐\n📞 +234 811 223 3445\n\nETA: *22 minutes*" }])}
              className="w-full py-2.5 rounded-xl font-bold text-white text-[11px]"
              style={{ background: WA_GREEN, fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Track Delivery 📍
            </button>
          </div>
        );

      case "tracking":
        return (
          <div className="p-3 space-y-2">
            {[["🏪 Restaurant", "Order ready"], ["🏍️ Rider", "Emeka O. en route"], ["📍 Your location", "14 min away"]].map(([k, v]) => (
              <div key={k as string} className="flex justify-between items-center px-3 py-2 rounded-xl border" style={{ background: "#1F2C34", borderColor: "rgba(255,255,255,0.08)" }}>
                <span className="text-[11px] text-white/60" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{k}</span>
                <span className="text-[11px] font-semibold text-[#25D366]" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{v}</span>
              </div>
            ))}
            <button onClick={() => go("review", "Order Delivered ✅", [{ side: "bot", text: "🎉 *Delivered!* We hope you enjoy your meal.\n\nHow would you rate this experience?\n\n⭐ Tap a star to rate:" }])}
              className="w-full py-2.5 rounded-xl font-bold text-white text-[11px] mt-1"
              style={{ background: "#E01E37", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Mark as Delivered ✅
            </button>
          </div>
        );

      case "review":
        return (
          <div className="p-4 text-center space-y-3">
            <div className="text-[12px] text-white/60 mb-2" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Rate your order</div>
            <div className="flex justify-center gap-2">
              {[1, 2, 3, 4, 5].map(s => (
                <button key={s} onClick={() => setReview(s)}>
                  <Star size={28} fill={s <= review ? "#C9A84C" : "transparent"} stroke={s <= review ? "#C9A84C" : "rgba(255,255,255,0.2)"} />
                </button>
              ))}
            </div>
            {review > 0 && (
              <button onClick={() => go("review_done", `${review} stars ⭐`, [{ side: "bot", text: `Thank you for rating ${review} ⭐!\n\nYour feedback helps us improve. Order again anytime — just say *Hey!* 👋\n\nEnjoy your meal! 🍽️` }])}
                className="w-full py-2.5 rounded-xl font-bold text-white text-[11px]"
                style={{ background: "#E01E37", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                Submit Review
              </button>
            )}
          </div>
        );

      case "review_done":
        return (
          <div className="p-4 text-center space-y-3">
            <div className="text-3xl">🎉</div>
            <div className="text-white font-bold text-sm" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>Thanks for the review!</div>
            <button onClick={() => { setScreen("customer_home"); setHistory(prev => [...prev, { side: "bot", text: "Welcome back! What can I get for you today? 🍽️" }]); }}
              className="w-full py-2.5 rounded-xl font-bold text-white text-[11px]"
              style={{ background: WA_GREEN, fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              Order Again
            </button>
          </div>
        );

      case "restaurant_home":
        return (
          <div className="p-3 space-y-2">
            <div className="text-[10px] text-white/30 text-center mb-2 uppercase tracking-widest">Restaurant Menu</div>
            {[
              { label: "📋 View / Edit Menu", msg: "You can update your menu by sending updated item details anytime. Format:\nItem Name | Price | Category | Description" },
              { label: "📦 Manage Orders", msg: "You have *3 pending orders*:\n\n1. #8841 — Jollof Rice ×2 (Adunola)\n2. #8842 — Egusi + Eba ×1 (Chidi)\n3. #8843 — Pepper Soup ×1 (Amaka)\n\nReply with order number to accept/reject." },
              { label: "🕐 Update Hours", msg: "Current hours:\n*Mon–Fri:* 8am – 9pm\n*Sat–Sun:* 10am – 8pm\n\nSend new hours to update." },
              { label: "💰 View Payouts", msg: "This week's earnings:\n\n• Orders: 47\n• Revenue: ₦141,500\n• Payout (Fri): ₦127,350\n\nDirect to your GTBank account." },
            ].map(o => (
              <button key={o.label} onClick={() => go("restaurant_home", o.label, [{ side: "bot", text: o.msg }])}
                className="w-full text-left px-3 py-2.5 rounded-xl text-[11px] font-semibold text-white border transition-colors hover:opacity-80"
                style={{ background: "rgba(37,211,102,0.06)", borderColor: "rgba(37,211,102,0.15)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                {o.label}
              </button>
            ))}
          </div>
        );

      case "rider_home":
        return (
          <div className="p-3 space-y-2">
            <div className="text-[10px] text-white/30 text-center mb-2 uppercase tracking-widest">Rider Menu</div>
            {[
              { label: "✅ Set Available", msg: "You're now *available* for deliveries in Lagos Island. You'll receive job notifications shortly." },
              { label: "🔴 Go Offline", msg: "You're now *offline*. You won't receive new delivery requests until you go available again." },
              { label: "📍 View Pending Jobs", msg: "Nearby jobs:\n\n1. Mama Nkechi's → 14 Karimu Kotun\n   ₦1,200 · 3.2km\n\n2. Lagos Grill → 5 Adeola Odeku\n   ₦900 · 2.1km\n\nReply with job number to accept." },
              { label: "💰 My Earnings", msg: "This week:\n\n• Deliveries: 23\n• Gross: ₦24,150\n• Wallet balance: ₦18,400\n\nWithdraw anytime via Nomba wallet." },
            ].map(o => (
              <button key={o.label} onClick={() => go("rider_home", o.label, [{ side: "bot", text: o.msg }])}
                className="w-full text-left px-3 py-2.5 rounded-xl text-[11px] font-semibold text-white border transition-colors hover:opacity-80"
                style={{ background: "rgba(201,168,76,0.06)", borderColor: "rgba(201,168,76,0.15)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                {o.label}
              </button>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <section id="whatsapp" className="py-24 px-6" style={{ background: "#0F0F0F" }}>
      <div className="max-w-6xl mx-auto">
        <SectionHeader
          tag="Live Prototype"
          title="Try the Deli experience"
          sub="Tap through the real WhatsApp flow — from first message to delivered order."
        />

        <div className="flex flex-col lg:flex-row gap-12 items-start justify-center">
          {/* Phone mockup */}
          <div className="mx-auto" style={{ width: "320px" }}>
            <div className="relative rounded-[40px] overflow-hidden shadow-2xl" style={{ background: "#1C1C1E", border: "8px solid #2C2C2E", height: "640px", display: "flex", flexDirection: "column" }}>
              {/* Notch */}
              <div className="flex justify-center pt-2 pb-1" style={{ background: WA_DARK }}>
                <div className="w-24 h-5 rounded-full" style={{ background: "#1C1C1E" }} />
              </div>

              {/* WA Header */}
              <div className="flex items-center gap-3 px-4 py-3" style={{ background: WA_HEADER }}>
                <button onClick={() => { setScreen("welcome"); setHistory([{ side: "bot", text: "👋 Welcome to *Deli* — your WhatsApp food marketplace in Lagos!" }, { side: "bot", text: "What brings you here today?" }]); setCart([]); }} className="text-white/60 hover:text-white">
                  <ArrowLeft size={16} />
                </button>
                <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: "#E01E37" }}>
                  <span className="text-white text-sm font-black" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>d</span>
                </div>
                <div className="flex-1">
                  <div className="text-white text-[13px] font-semibold" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Deli 🍽️</div>
                  <div className="text-[10px]" style={{ color: WA_GREEN, fontFamily: "'Plus Jakarta Sans', sans-serif" }}>online</div>
                </div>
                <div className="flex gap-3 text-white/50">
                  <Phone size={15} />
                  <MoreVertical size={15} />
                </div>
              </div>

              {/* Chat area */}
              <div ref={chatRef} className="flex-1 overflow-y-auto px-3 py-3 space-y-0.5" style={{ background: WA_DARK, scrollbarWidth: "none" }}>
                {history.map((m, i) => <WaMsg key={i} side={m.side} text={m.text} />)}
              </div>

              {/* Interactive options */}
              <div style={{ background: WA_DARK, borderTop: "1px solid rgba(255,255,255,0.06)" }}>
                {renderScreen()}
              </div>

              {/* Bottom input bar */}
              <div className="flex items-center gap-2 px-3 py-2" style={{ background: WA_HEADER }}>
                <div className="flex-1 rounded-full px-4 py-2 text-[11px] text-white/30" style={{ background: "#2A3942", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                  Message
                </div>
                <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: WA_GREEN }}>
                  <Send size={12} className="text-white" />
                </div>
              </div>
            </div>
          </div>

          {/* Explainer */}
          <div className="flex-1 max-w-md space-y-6 pt-4">
            <h3 className="text-white font-black text-2xl" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>
              The full ordering journey,<br />inside WhatsApp.
            </h3>
            <div className="space-y-4">
              {[
                { icon: MessageSquare, title: "No app to install", desc: "Customers order entirely inside WhatsApp using interactive menus and buttons.", color: "#25D366" },
                { icon: Store, title: "Restaurant control panel", desc: "Restaurants manage menus, hours, and orders via WhatsApp commands or the admin dashboard.", color: "#E01E37" },
                { icon: Bike, title: "Rider coordination", desc: "Riders receive jobs, confirm pickups, and get paid — all coordinated through WhatsApp.", color: "#C9A84C" },
              ].map(item => (
                <div key={item.title} className="flex gap-4 items-start">
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0" style={{ background: `${item.color}18` }}>
                    <item.icon size={16} style={{ color: item.color }} />
                  </div>
                  <div>
                    <div className="text-white font-bold text-sm mb-1" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{item.title}</div>
                    <div className="text-sm text-white/50 leading-relaxed" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{item.desc}</div>
                  </div>
                </div>
              ))}
            </div>
            <div className="pt-2">
              <div className="text-xs text-white/30 mb-2 uppercase tracking-widest" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Prototype progress</div>
              <div className="flex gap-2 flex-wrap">
                {(["welcome", "customer_home", "browse_restaurants", "restaurant_menu", "item_detail", "cart", "delivery_details", "payment", "order_success", "tracking", "review"] as WAScreen[]).map(s => (
                  <div key={s} className="w-2.5 h-2.5 rounded-full transition-all" style={{ background: s === screen ? "#E01E37" : history.some(h => h.text.includes("order")) ? "rgba(255,255,255,0.2)" : "rgba(255,255,255,0.1)" }} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ─── Admin Dashboard ──────────────────────────────────────────────────────────

function AdminDashboard() {
  const [role, setRole] = useState<"restaurant" | "rider">("restaurant");
  const [tab, setTab] = useState("overview");

  const restaurantTabs = ["overview", "inventory", "orders", "payouts"];
  const riderTabs = ["overview", "jobs", "earnings"];

  const tabs = role === "restaurant" ? restaurantTabs : riderTabs;

  useEffect(() => { setTab("overview"); }, [role]);

  return (
    <section id="admin" className="py-24 px-6" style={{ background: "#F5F3F0" }}>
      <div className="max-w-6xl mx-auto">
        <SectionHeader
          tag="Partner Dashboard"
          title="Everything you need, one place"
          sub="Restaurants and riders get a clean management dashboard alongside WhatsApp control."
          light
        />

        {/* Role selector */}
        <div className="flex justify-center mb-8">
          <div className="flex gap-1 p-1 rounded-2xl" style={{ background: "#E8E5E0" }}>
            {[["restaurant", "🏪 Restaurant"], ["rider", "🏍️ Rider"]].map(([r, label]) => (
              <button key={r} onClick={() => setRole(r as "restaurant" | "rider")}
                className="px-6 py-2.5 rounded-xl font-semibold text-sm transition-all"
                style={{
                  background: role === r ? "#0A0A0A" : "transparent",
                  color: role === r ? "#F0EDE8" : "#555",
                  fontFamily: "'Plus Jakarta Sans', sans-serif",
                }}>
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-3xl overflow-hidden border" style={{ background: "#0A0A0A", borderColor: "rgba(255,255,255,0.06)" }}>
          {/* Dashboard nav */}
          <div className="flex items-center justify-between px-6 py-4 border-b" style={{ borderColor: "rgba(255,255,255,0.06)", background: "#111111" }}>
            <div className="flex items-center gap-6">
              <DeliLogo dark />
              <div className="flex gap-1">
                {tabs.map(t => (
                  <button key={t} onClick={() => setTab(t)}
                    className="px-4 py-1.5 rounded-lg text-sm font-semibold capitalize transition-all"
                    style={{ background: tab === t ? "#E01E37" : "transparent", color: tab === t ? "white" : "rgba(240,237,232,0.5)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                    {t}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "#1A1A1A" }}>
                <Bell size={14} className="text-white/50" />
              </button>
              <div className="w-8 h-8 rounded-full bg-[#E01E37] flex items-center justify-center text-white text-xs font-bold" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>
                {role === "restaurant" ? "NK" : "EO"}
              </div>
            </div>
          </div>

          {/* Dashboard content */}
          <div className="p-6">
            {role === "restaurant" && tab === "overview" && (
              <div className="space-y-6">
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {[["₦141,500", "Revenue this week", TrendingUp, "#25D366", "+12%"], ["47", "Orders today", ShoppingCart, "#E01E37", "+3"], ["4.8 ★", "Restaurant rating", Star, "#C9A84C", "Top 5%"], ["18 min", "Avg prep time", Clock, "#25D366", "on target"]].map(([val, label, Icon, color, sub]) => (
                    <div key={label as string} className="rounded-2xl p-5 border" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
                      <Icon size={18} style={{ color, marginBottom: 12 }} />
                      <div className="text-2xl font-black text-white mb-0.5" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{val}</div>
                      <div className="text-xs text-white/40 mb-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{label}</div>
                      <div className="text-xs font-semibold" style={{ color, fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{sub}</div>
                    </div>
                  ))}
                </div>

                {/* Recent orders */}
                <div className="rounded-2xl border overflow-hidden" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
                  <div className="px-5 py-4 border-b" style={{ borderColor: "rgba(255,255,255,0.07)" }}>
                    <h4 className="font-bold text-white text-sm" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>Recent Orders</h4>
                  </div>
                  {[
                    { id: "#8844", customer: "Adunola M.", items: "Jollof Rice ×2, Plantain ×1", total: "₦6,200", status: "Preparing", color: "#C9A84C" },
                    { id: "#8843", customer: "Chidi O.", items: "Egusi + Eba ×1", total: "₦3,200", status: "Ready", color: "#25D366" },
                    { id: "#8842", customer: "Amaka F.", items: "Pepper Soup ×1", total: "₦3,800", status: "Delivered", color: "#444" },
                  ].map(o => (
                    <div key={o.id} className="flex items-center justify-between px-5 py-4 border-b border-white/5 last:border-0">
                      <div>
                        <div className="text-sm font-semibold text-white" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{o.id} · {o.customer}</div>
                        <div className="text-xs text-white/40 mt-0.5" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{o.items}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-white" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{o.total}</div>
                        <div className="text-xs font-semibold mt-0.5" style={{ color: o.color, fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{o.status}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {role === "restaurant" && tab === "inventory" && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h4 className="font-bold text-white" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>Menu Items</h4>
                  <button className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white" style={{ background: "#E01E37", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                    <Plus size={14} /> Add Item
                  </button>
                </div>
                {MENU_ITEMS[1].map(item => (
                  <div key={item.id} className="flex items-center gap-4 p-4 rounded-2xl border" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
                    <div className="w-12 h-12 rounded-xl overflow-hidden bg-[#1A1A1A] shrink-0">
                      <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-bold text-white" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{item.name}</div>
                      <div className="text-xs text-white/40 mt-0.5" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>⭐ {item.rating}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-base font-black text-[#E01E37]" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>₦{item.price.toLocaleString()}</div>
                      <div className="text-xs font-semibold mt-1" style={{ color: "#25D366", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Available</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {role === "restaurant" && tab === "orders" && (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4 mb-4">
                  {[["12", "Pending", "#E01E37"], ["8", "In Progress", "#C9A84C"], ["27", "Completed", "#25D366"]].map(([n, l, c]) => (
                    <div key={l} className="rounded-2xl p-4 text-center border" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
                      <div className="text-3xl font-black mb-1" style={{ color: c as string, fontFamily: "'Bricolage Grotesque', sans-serif" }}>{n}</div>
                      <div className="text-xs text-white/40" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{l}</div>
                    </div>
                  ))}
                </div>
                {[{ id: "#8848", c: "Tunde A.", items: "Suya Platter ×1", t: "₦4,500", s: "Pending", age: "2 min ago" }, { id: "#8847", c: "Ngozi B.", items: "Jollof Rice ×3", t: "₦7,500", s: "Pending", age: "5 min ago" }].map(o => (
                  <div key={o.id} className="p-5 rounded-2xl border" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <div className="text-sm font-bold text-white" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{o.id} · {o.c}</div>
                        <div className="text-xs text-white/40 mt-0.5" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{o.items} · {o.age}</div>
                      </div>
                      <div className="font-black text-[#E01E37]" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{o.t}</div>
                    </div>
                    <div className="flex gap-2">
                      <button className="flex-1 py-2 rounded-xl text-xs font-bold text-white" style={{ background: "#25D366", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Accept</button>
                      <button className="flex-1 py-2 rounded-xl text-xs font-bold text-white/60 border border-white/10" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Reject</button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {role === "restaurant" && tab === "payouts" && (
              <div className="space-y-4">
                <div className="rounded-2xl p-6 border" style={{ background: "linear-gradient(135deg, #1A0508, #1A1A1A)", borderColor: "rgba(224,30,55,0.15)" }}>
                  <div className="text-xs text-[#C9A84C] font-bold mb-2 uppercase tracking-widest" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Pending Payout</div>
                  <div className="text-4xl font-black text-white mb-1" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>₦127,350</div>
                  <div className="text-sm text-white/50" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Arrives Friday 11 July · GTBank ••••4423</div>
                </div>
                {[["This week", "₦141,500", "47 orders", "#25D366"], ["Last week", "₦98,200", "33 orders", "#C9A84C"], ["2 weeks ago", "₦115,800", "39 orders", "#C9A84C"]].map(([period, amount, orders, c]) => (
                  <div key={period} className="flex justify-between items-center p-5 rounded-2xl border" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
                    <div>
                      <div className="text-sm font-semibold text-white" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{period}</div>
                      <div className="text-xs text-white/40 mt-0.5" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{orders}</div>
                    </div>
                    <div className="font-black text-xl" style={{ color: c as string, fontFamily: "'Bricolage Grotesque', sans-serif" }}>{amount}</div>
                  </div>
                ))}
              </div>
            )}

            {role === "rider" && tab === "overview" && (
              <div className="space-y-6">
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {[["₦18,400", "Wallet balance", Wallet, "#C9A84C"], ["23", "Deliveries today", Truck, "#25D366"], ["4.9 ★", "Your rating", Star, "#C9A84C"], ["Available", "Status", Circle, "#25D366"]].map(([val, label, Icon, color]) => (
                    <div key={label as string} className="rounded-2xl p-5 border" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
                      <Icon size={18} style={{ color, marginBottom: 12 }} />
                      <div className="text-2xl font-black text-white mb-0.5" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{val}</div>
                      <div className="text-xs text-white/40" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{label}</div>
                    </div>
                  ))}
                </div>
                <div className="rounded-2xl border overflow-hidden" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
                  <div className="px-5 py-4 border-b" style={{ borderColor: "rgba(255,255,255,0.07)" }}>
                    <h4 className="font-bold text-white text-sm" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>Recent Deliveries</h4>
                  </div>
                  {[["Mama Nkechi's → V.I.", "Adunola M.", "₦1,200", "Just now"], ["Lagos Grill → Lekki", "Tunde A.", "₦900", "1h ago"], ["Iya Basira → Surulere", "Ngozi B.", "₦1,400", "3h ago"]].map(([route, cust, fee, time]) => (
                    <div key={route as string} className="flex items-center justify-between px-5 py-4 border-b border-white/5 last:border-0">
                      <div>
                        <div className="text-sm font-semibold text-white" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{route}</div>
                        <div className="text-xs text-white/40 mt-0.5" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{cust} · {time}</div>
                      </div>
                      <div className="font-black text-[#25D366]" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{fee}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {role === "rider" && tab === "jobs" && (
              <div className="space-y-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold text-white" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>Pending Near You</h4>
                  <div className="flex items-center gap-2 text-xs font-semibold text-[#25D366]" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                    <div className="w-2 h-2 rounded-full bg-[#25D366]" /> Available
                  </div>
                </div>
                {[{ from: "Mama Nkechi's Kitchen", to: "14 Karimu Kotun St, V.I.", dist: "3.2km", fee: "₦1,200", eta: "8 min" }, { from: "Lagos Grill House", to: "5 Adeola Odeku, V.I.", dist: "2.1km", fee: "₦900", eta: "5 min" }, { from: "Iya Basira Spot", to: "22 Awolowo Road, Ikoyi", dist: "4.5km", fee: "₦1,500", eta: "12 min" }].map((job, i) => (
                  <div key={i} className="p-5 rounded-2xl border" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Store size={12} className="text-[#E01E37]" />
                          <span className="text-xs font-semibold text-white/70" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{job.from}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <MapPin size={12} className="text-[#C9A84C]" />
                          <span className="text-xs text-white/50" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{job.to}</span>
                        </div>
                      </div>
                      <div className="text-right shrink-0 ml-4">
                        <div className="font-black text-lg text-[#25D366]" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{job.fee}</div>
                        <div className="text-[10px] text-white/40" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{job.dist} · {job.eta}</div>
                      </div>
                    </div>
                    <button className="w-full py-2 rounded-xl text-xs font-bold text-white" style={{ background: "#E01E37", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                      Accept Job
                    </button>
                  </div>
                ))}
              </div>
            )}

            {role === "rider" && tab === "earnings" && (
              <div className="space-y-4">
                <div className="rounded-2xl p-6 border" style={{ background: "linear-gradient(135deg, #0A120A, #1A1A1A)", borderColor: "rgba(37,211,102,0.15)" }}>
                  <div className="text-xs text-[#25D366] font-bold mb-2 uppercase tracking-widest" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Wallet Balance</div>
                  <div className="text-4xl font-black text-white mb-1" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>₦18,400</div>
                  <button className="mt-3 px-5 py-2 rounded-xl text-xs font-bold text-white" style={{ background: "#25D366", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Withdraw to Bank</button>
                </div>
                {[["This week", "₦24,150", "23 deliveries"], ["Last week", "₦19,800", "18 deliveries"], ["2 weeks ago", "₦22,400", "21 deliveries"]].map(([period, amount, cnt]) => (
                  <div key={period} className="flex justify-between items-center p-5 rounded-2xl border" style={{ background: "#141414", borderColor: "rgba(255,255,255,0.07)" }}>
                    <div>
                      <div className="text-sm font-semibold text-white" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{period}</div>
                      <div className="text-xs text-white/40 mt-0.5" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{cnt}</div>
                    </div>
                    <div className="font-black text-xl text-[#25D366]" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{amount}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function AdminPage({ onBack, onCta }: { onBack: () => void; onCta: () => void }) {
  return (
    <div className="min-h-screen" style={{ background: "#0A0A0A" }}>
      <header className="sticky top-0 z-50 bg-white border-b border-gray-100" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
        <div className="max-w-6xl mx-auto h-16 px-6 flex items-center justify-between">
          <button onClick={onBack} className="flex items-center gap-3 group">
            <ArrowLeft size={18} className="text-[#E01E37] transition-transform group-hover:-translate-x-1" />
            <DeliLogo />
          </button>
          <div className="flex items-center gap-3">
            <button onClick={onCta} className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-full text-sm font-bold text-white transition-all hover:scale-105" style={{ background: "linear-gradient(135deg, #E01E37 0%, #C01530 100%)" }}>
              <MessageSquare size={15} />
              Open WhatsApp
            </button>
            <button onClick={onBack} className="px-4 py-2 rounded-full text-sm font-bold border border-gray-200 text-[#0A0A0A] hover:border-[#E01E37] hover:text-[#E01E37] transition-colors">
              Public site
            </button>
          </div>
        </div>
      </header>

      <section className="pt-16 px-6 pb-8" style={{ background: "#0A0A0A" }}>
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-[1.15fr_.85fr] gap-10 items-end">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full mb-6" style={{ background: "rgba(224,30,55,0.12)", border: "1px solid rgba(224,30,55,0.24)" }}>
                <Settings size={14} className="text-[#E01E37]" />
                <span className="text-xs font-bold uppercase tracking-widest text-[#E01E37]" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Partner admin</span>
              </div>
              <h1 className="text-5xl sm:text-6xl font-black leading-[0.95] text-white mb-5" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>
                Run the food side of Deli without opening Django admin.
              </h1>
              <p className="text-lg text-white/55 leading-relaxed max-w-2xl" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                Restaurants can manage menus, availability, orders and payouts. Riders can manage availability, delivery jobs and earnings. This is the simple dashboard experience partners see after login.
              </p>
            </div>
            <div className="rounded-3xl p-5 border" style={{ background: "linear-gradient(135deg, rgba(224,30,55,.16), rgba(255,255,255,.04))", borderColor: "rgba(255,255,255,.08)" }}>
              {[
                ["Restaurant", "Accept orders, update menu items, mark sold out, review payouts.", Store],
                ["Rider", "Set available, accept nearby jobs, confirm delivery, track wallet.", Bike],
                ["Deli Admin", "Use Django admin for approvals, edits and deeper operations.", Shield],
              ].map(([title, desc, Icon]) => (
                <div key={title as string} className="flex gap-4 py-4 border-b border-white/5 last:border-0">
                  <div className="w-10 h-10 rounded-2xl flex items-center justify-center shrink-0" style={{ background: "#E01E37" }}>
                    <Icon size={18} className="text-white" />
                  </div>
                  <div>
                    <div className="font-bold text-white" style={{ fontFamily: "'Bricolage Grotesque', sans-serif" }}>{title}</div>
                    <div className="text-sm text-white/50 leading-relaxed" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <AdminDashboard />
      <Footer onCta={onCta} />
    </div>
  );
}

// ─── Footer ───────────────────────────────────────────────────────────────────

function Footer({ onCta }: { onCta: () => void }) {
  return (
    <footer style={{ background: "#0A0A0A", borderTop: "1px solid rgba(255,255,255,0.06)" }}>
      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-12 mb-12">
          <div className="lg:col-span-2">
            <DeliLogo dark />
            <p className="text-white/50 text-sm mt-4 leading-relaxed max-w-xs" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              The WhatsApp-first food ordering marketplace for Lagos. Order, deliver, and manage — no app required.
            </p>
            <button onClick={onCta} className="mt-6 flex items-center gap-2 px-6 py-3 rounded-full font-bold text-white text-sm transition-all hover:scale-105" style={{ background: "linear-gradient(135deg, #E01E37 0%, #C01530 100%)", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z" /></svg>
              Start ordering now
            </button>
          </div>
          <div>
            <div className="text-xs font-bold uppercase tracking-widest text-white/30 mb-4" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Platform</div>
            {["How it works", "Browse restaurants", "Track order", "Pricing"].map(l => (
              <div key={l} className="text-sm text-white/50 mb-2 hover:text-white/80 cursor-pointer transition-colors" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{l}</div>
            ))}
          </div>
          <div>
            <div className="text-xs font-bold uppercase tracking-widest text-white/30 mb-4" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Partners</div>
            {["Register restaurant", "Become a rider", "Partner dashboard", "Support"].map(l => (
              <div key={l} className="text-sm text-white/50 mb-2 hover:text-white/80 cursor-pointer transition-colors" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{l}</div>
            ))}
          </div>
        </div>
        <div className="flex flex-col sm:flex-row items-center justify-between pt-8 border-t border-white/5">
          <div className="text-xs text-white/30" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>© 2025 Deli. All rights reserved. Lagos, Nigeria.</div>
          <div className="flex items-center gap-2 mt-4 sm:mt-0">
            <Shield size={12} className="text-[#C9A84C]" />
            <span className="text-xs text-white/30" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Payments secured by <span className="text-[#C9A84C]">Nomba</span></span>
          </div>
        </div>
      </div>
    </footer>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────

export default function App() {
  const WA_NUMBER = import.meta.env.VITE_WHATSAPP_NUMBER || "2347089823013";
  const WA_MSG = encodeURIComponent("Hey Deli! I want to order food 🍽️");
  const WA_URL = `https://wa.me/${WA_NUMBER}?text=${WA_MSG}`;
  const [page, setPage] = useState<"home" | "admin">(
    window.location.hash === "#partner-admin" ? "admin" : "home"
  );

  useEffect(() => {
    const handleHashChange = () => {
      setPage(window.location.hash === "#partner-admin" ? "admin" : "home");
    };

    window.addEventListener("hashchange", handleHashChange);

    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const openAdmin = () => {
    window.location.hash = "partner-admin";
    setPage("admin");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const openHome = () => {
    window.location.hash = "";
    setPage("home");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const scrollTo = (id: string) => {
    if (page !== "home") {
      setPage("home");
      window.location.hash = "";
      setTimeout(() => {
        const el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 0);
      return;
    }

    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  if (page === "admin") {
    return (
      <AdminPage
        onBack={openHome}
        onCta={() => window.open(WA_URL, "_blank")}
      />
    );
  }

  return (
    <div className="min-h-screen" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", background: "#0A0A0A" }}>
      <TopNav
        onCtaClick={() => window.open(WA_URL, "_blank")}
        onScrollTo={scrollTo}
        onAdminClick={openAdmin}
      />
      <main>
        <HeroSection onCta={() => window.open(WA_URL, "_blank")} onScrollTo={scrollTo} />
        <CustomerSection />
        <RestaurantSection onCta={() => window.open(WA_URL, "_blank")} />
        <RiderSection onCta={() => window.open(WA_URL, "_blank")} />
        <PaymentSection />
        <WhatsAppPrototype />
        <AdminDashboard />
      </main>
      <Footer onCta={() => window.open(WA_URL, "_blank")} />
    </div>
  );
}
