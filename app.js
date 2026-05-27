/* ==============================================================
   CORE DASHBOARD APPLICATION LOGIC - SALES INTELLIGENCE SYSTEM
   ============================================================== */

document.addEventListener("DOMContentLoaded", () => {
    console.log("Dashboard engine initialized.");
    
    // Globals
    let charts = {};
    
    // Check if data is loaded successfully
    if (typeof SalesDashboardData === 'undefined') {
        console.error("SalesDashboardData is missing. Ensure dashboard/data_store.js is loaded first.");
        return;
    }

    const dataStore = SalesDashboardData;
    const transactions = dataStore.raw_transactions;

    // Elements
    const tabButtons = document.querySelectorAll(".nav-item");
    const tabContents = document.querySelectorAll(".tab-content");
    const regionFilter = document.getElementById("filter-region");
    const categoryFilter = document.getElementById("filter-category");
    const loyaltyFilter = document.getElementById("filter-loyalty");
    const resetFiltersBtn = document.getElementById("reset-filters-btn");
    
    // Advisor Elements
    const advRegion = document.getElementById("adv-region");
    const advCategory = document.getElementById("adv-category");
    const runDiagnosticsBtn = document.getElementById("run-diagnostics-btn");
    
    // -------------------------------------------------------------
    // Tab Switching Mechanics
    // -------------------------------------------------------------
    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");
            
            // Toggle buttons
            tabButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            // Toggle contents
            tabContents.forEach(content => {
                content.classList.remove("active");
                if (content.id === `tab-${targetTab}`) {
                    content.classList.add("active");
                }
            });
            
            // Redraw charts if needed for spacing/responsiveness
            setTimeout(() => {
                Object.keys(charts).forEach(key => {
                    charts[key].resize();
                    charts[key].update();
                });
            }, 50);
        });
    });

    // -------------------------------------------------------------
    // Filtering and Recalculations
    // -------------------------------------------------------------
    function getFilteredData() {
        const selRegion = regionFilter.value;
        const selCategory = categoryFilter.value;
        const selLoyalty = loyaltyFilter.value;

        return transactions.filter(t => {
            const matchRegion = (selRegion === "ALL" || t.region === selRegion);
            const matchCategory = (selCategory === "ALL" || t.category === selCategory);
            const matchLoyalty = (selLoyalty === "ALL" || t.repeat === selLoyalty);
            return matchRegion && matchCategory && matchLoyalty;
        });
    }

    function calculateAndDisplayKPIs(filtered) {
        let revenue = 0;
        let profit = 0;
        let ordersSet = new Set();
        
        filtered.forEach(t => {
            revenue += t.sales;
            profit += t.profit;
            ordersSet.add(t.order_id);
        });

        const margin = revenue > 0 ? (profit / revenue) * 100 : 0;
        const totalOrders = ordersSet.size;

        // Display
        document.querySelector("#kpi-revenue .kpi-value").textContent = `$${revenue.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        document.querySelector("#kpi-profit .kpi-value").textContent = `$${profit.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        document.querySelector("#kpi-margin .kpi-value").textContent = `${margin.toFixed(1)}%`;
        document.querySelector("#kpi-orders .kpi-value").textContent = totalOrders.toLocaleString('en-US');
    }

    // -------------------------------------------------------------
    // Charts Render Engines
    // -------------------------------------------------------------
    
    // Helper to clear existing chart instance
    function safeInitChart(canvasId, config) {
        if (charts[canvasId]) {
            charts[canvasId].destroy();
        }
        const ctx = document.getElementById(canvasId).getContext("2d");
        charts[canvasId] = new Chart(ctx, config);
    }

    function renderSummaryTrends(filtered) {
        // We aggregate the filtered subset by month-year
        // Create an ordered map of year-month dates
        const monthlyAgg = {};
        
        // Populate standard labels to keep timeline continuous
        dataStore.historical_sales_monthly.forEach(h => {
            monthlyAgg[h.Month] = { sales: 0, profit: 0 };
        });

        filtered.forEach(t => {
            // Extract YYYY-MM
            const ym = t.date.substring(0, 7);
            if (monthlyAgg[ym]) {
                monthlyAgg[ym].sales += t.sales;
                monthlyAgg[ym].profit += t.profit;
            }
        });

        const labels = Object.keys(monthlyAgg).sort();
        const salesData = labels.map(l => monthlyAgg[l].sales);
        const profitData = labels.map(l => monthlyAgg[l].profit);

        safeInitChart("chart-summary-trends", {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Revenue ($)",
                        data: salesData,
                        borderColor: "#6366f1",
                        backgroundColor: "rgba(99, 102, 241, 0.1)",
                        fill: true,
                        tension: 0.3,
                        yAxisID: "y-sales",
                        borderWidth: 2
                    },
                    {
                        label: "Profit ($)",
                        data: profitData,
                        borderColor: "#10b981",
                        backgroundColor: "transparent",
                        fill: false,
                        tension: 0.3,
                        yAxisID: "y-profit",
                        borderWidth: 2,
                        borderDash: [4, 4]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "top", labels: { color: "#94a3b8" } }
                },
                scales: {
                    x: { grid: { color: "rgba(255,255,255,0.03)" }, ticks: { color: "#94a3b8" } },
                    "y-sales": {
                        type: "linear",
                        position: "left",
                        title: { display: true, text: "Sales ($)", color: "#6366f1" },
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: { color: "#94a3b8" }
                    },
                    "y-profit": {
                        type: "linear",
                        position: "right",
                        title: { display: true, text: "Profit ($)", color: "#10b981" },
                        grid: { drawOnChartArea: false },
                        ticks: { color: "#94a3b8" }
                    }
                }
            }
        });
    }

    function renderSummaryCategoryPie(filtered) {
        const catMap = { "Electronics": 0, "Furniture": 0, "Office Supplies": 0 };
        filtered.forEach(t => {
            if (catMap[t.category] !== undefined) {
                catMap[t.category] += t.sales;
            }
        });

        safeInitChart("chart-summary-categories", {
            type: "doughnut",
            data: {
                labels: Object.keys(catMap),
                datasets: [{
                    data: Object.values(catMap),
                    backgroundColor: ["#6366f1", "#a855f7", "#ec4899"],
                    borderWidth: 2,
                    borderColor: "#1e293b"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom", labels: { color: "#94a3b8", padding: 12 } }
                },
                cutout: "60%"
            }
        });
    }

    function renderSalesRegional(filtered) {
        const regMap = { "Central": 0, "East": 0, "South": 0, "West": 0 };
        filtered.forEach(t => {
            if (regMap[t.region] !== undefined) {
                regMap[t.region] += t.sales;
            }
        });

        safeInitChart("chart-sales-regional", {
            type: "pie",
            data: {
                labels: Object.keys(regMap),
                datasets: [{
                    data: Object.values(regMap),
                    backgroundColor: ["#38bdf8", "#6366f1", "#ec4899", "#10b981"],
                    borderWidth: 2,
                    borderColor: "#1e293b"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom", labels: { color: "#94a3b8", padding: 12 } }
                }
            }
        });
    }

    function renderSalesSubcategories(filtered) {
        const subcatData = {};
        filtered.forEach(t => {
            if (!subcatData[t.subcat]) {
                subcatData[t.subcat] = { sales: 0, profit: 0 };
            }
            subcatData[t.subcat].sales += t.sales;
            subcatData[t.subcat].profit += t.profit;
        });

        // Sort by sales descending
        const sortedSubcats = Object.keys(subcatData).sort((a,b) => subcatData[b].sales - subcatData[a].sales).slice(0, 10);
        const salesData = sortedSubcats.map(s => subcatData[s].sales);
        const marginData = sortedSubcats.map(s => subcatData[s].sales > 0 ? (subcatData[s].profit / subcatData[s].sales) * 100 : 0);

        safeInitChart("chart-sales-subcategories", {
            type: "bar",
            data: {
                labels: sortedSubcats,
                datasets: [
                    {
                        label: "Sales ($)",
                        data: salesData,
                        backgroundColor: "#6366f1",
                        yAxisID: "y-sales",
                        borderRadius: 4
                    },
                    {
                        label: "Net Margin (%)",
                        data: marginData,
                        borderColor: "#ec4899",
                        backgroundColor: "rgba(236, 72, 153, 0.2)",
                        type: "line",
                        tension: 0.3,
                        yAxisID: "y-margin",
                        borderWidth: 2,
                        pointRadius: 3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "top", labels: { color: "#94a3b8" } }
                },
                scales: {
                    x: { grid: { color: "rgba(255,255,255,0.03)" }, ticks: { color: "#94a3b8" } },
                    "y-sales": {
                        type: "linear",
                        position: "left",
                        title: { display: true, text: "Sales ($)", color: "#6366f1" },
                        grid: { color: "rgba(255,255,255,0.03)" },
                        ticks: { color: "#94a3b8" }
                    },
                    "y-margin": {
                        type: "linear",
                        position: "right",
                        title: { display: true, text: "Margin (%)", color: "#ec4899" },
                        grid: { drawOnChartArea: false },
                        ticks: { color: "#94a3b8" }
                    }
                }
            }
        });
    }

    function renderCustomerDays(filtered) {
        // Purchases by Day of week (Weekend vs Weekday)
        const dayMap = { "Weekday": 0, "Weekend": 0 };
        
        filtered.forEach(t => {
            // Determine day type
            const orderDate = new Date(t.date);
            const isWeekend = orderDate.getDay() === 0 || orderDate.getDay() === 6; // 0 = Sun, 6 = Sat
            const type = isWeekend ? "Weekend" : "Weekday";
            dayMap[type] += t.sales;
        });

        // Standard average order size by day type
        safeInitChart("chart-customer-days", {
            type: "bar",
            data: {
                labels: ["Weekdays (Mon-Fri)", "Weekends (Sat-Sun)"],
                datasets: [{
                    label: "Cumulative Sales ($)",
                    data: [dayMap["Weekday"], dayMap["Weekend"]],
                    backgroundColor: ["#a855f7", "#ec4899"],
                    borderRadius: 6,
                    barThickness: 50
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { grid: { color: "rgba(255,255,255,0.03)" }, ticks: { color: "#94a3b8" } },
                    x: { ticks: { color: "#94a3b8" } }
                }
            }
        });
    }

    // -------------------------------------------------------------
    // Customer Insights Details
    // -------------------------------------------------------------
    function renderCustomerLoyaltyGauge(filtered) {
        let repeatSales = 0;
        let firstSales = 0;
        let repeatCustomers = new Set();
        let allCustomers = new Set();
        
        filtered.forEach(t => {
            allCustomers.add(t.customer);
            if (t.repeat === "Yes") {
                repeatSales += t.sales;
                repeatCustomers.add(t.customer);
            } else {
                firstSales += t.sales;
            }
        });

        const loyaltyRate = allCustomers.size > 0 ? (repeatCustomers.size / allCustomers.size) * 100 : 0;
        
        // Display Gauge Text
        document.querySelector("#loyalty-rate-gauge .circle-val").textContent = `${loyaltyRate.toFixed(1)}%`;
        document.getElementById("loyalty-sales-repeat").textContent = `$${repeatSales.toLocaleString('en-US', {maximumFractionDigits: 0})}`;
        document.getElementById("loyalty-sales-first").textContent = `$${firstSales.toLocaleString('en-US', {maximumFractionDigits: 0})}`;
    }

    function renderCustomerLeaderboard(filtered) {
        const custData = {};
        filtered.forEach(t => {
            if (!custData[t.customer]) {
                custData[t.customer] = { orders: new Set(), qty: 0, spent: 0, profit: 0, repeat: "No" };
            }
            custData[t.customer].orders.add(t.order_id);
            custData[t.customer].qty += t.qty;
            custData[t.customer].spent += t.sales;
            custData[t.customer].profit += t.profit;
            if (t.repeat === "Yes") custData[t.customer].repeat = "Yes";
        });

        const sortedCustomers = Object.keys(custData)
            .map(name => ({
                name: name,
                orders: custData[name].orders.size,
                qty: custData[name].qty,
                spent: custData[name].spent,
                profit: custData[name].profit,
                repeat: custData[name].repeat
            }))
            .sort((a,b) => b.spent - a.spent)
            .slice(0, 8);

        const tbody = document.querySelector("#customer-leaderboard-table tbody");
        tbody.innerHTML = "";

        sortedCustomers.forEach((c, idx) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td><strong>#${idx + 1}</strong></td>
                <td><i class="fa-regular fa-user text-indigo" style="margin-right: 8px;"></i> ${c.name}</td>
                <td>${c.orders}</td>
                <td>${c.qty} units</td>
                <td>$${c.spent.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                <td class="${c.profit >= 0 ? 'text-emerald' : 'text-pink'}">$${c.profit.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                <td><span class="badge ${c.repeat === 'Yes' ? 'badge-repeat' : 'badge-first'}">${c.repeat === 'Yes' ? 'Repeat' : 'First-time'}</span></td>
            `;
            tbody.appendChild(row);
        });
    }

    // -------------------------------------------------------------
    // AI Forecasting Models Page
    // -------------------------------------------------------------
    function renderMLForecastChart() {
        const historical = dataStore.historical_sales_monthly;
        const forecasts = dataStore.forecast_12_months;
        
        const histLabels = historical.map(h => h.Month);
        const histSales = historical.map(h => h.Sales);
        
        const foreLabels = forecasts.map(f => f.Month);
        const lrSales = forecasts.map(f => f.Linear_Regression_Forecast);
        const rfSales = forecasts.map(f => f.Random_Forest_Forecast);

        // Continuous timeline construction
        const allLabels = [...histLabels, ...foreLabels];
        
        // Build datasets
        // Historical Actuals (only populated up to historical range)
        const dHist = allLabels.map((l, i) => i < histLabels.length ? histSales[i] : null);
        
        // Linear regression (populated only in forecast range, connected to last historical point)
        const dLR = allLabels.map((l, i) => {
            if (i === histLabels.length - 1) return histSales[histSales.length - 1];
            if (i >= histLabels.length) return lrSales[i - histLabels.length];
            return null;
        });

        // Random Forest (populated only in forecast range, connected to last historical point)
        const dRF = allLabels.map((l, i) => {
            if (i === histLabels.length - 1) return histSales[histSales.length - 1];
            if (i >= histLabels.length) return rfSales[i - histLabels.length];
            return null;
        });

        safeInitChart("chart-ml-forecast", {
            type: "line",
            data: {
                labels: allLabels,
                datasets: [
                    {
                        label: "Historical Actuals",
                        data: dHist,
                        borderColor: "#0f172a",
                        backgroundColor: "#6366f1",
                        pointBackgroundColor: "#0f172a",
                        borderWidth: 3,
                        pointRadius: 4,
                        fill: false
                    },
                    {
                        label: "Linear Regression Forecast",
                        data: dLR,
                        borderColor: "#6366f1",
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointStyle: "triangle",
                        pointRadius: 4,
                        fill: false
                    },
                    {
                        label: "Random Forest Forecast",
                        data: dRF,
                        borderColor: "#ec4899",
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointStyle: "rect",
                        pointRadius: 4,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: "#94a3b8" } }
                },
                scales: {
                    y: { grid: { color: "rgba(255,255,255,0.03)" }, ticks: { color: "#94a3b8" } },
                    x: { grid: { color: "rgba(255,255,255,0.03)" }, ticks: { color: "#94a3b8", maxRotation: 90, minRotation: 45 } }
                }
            }
        });
    }

    function renderForecastTable() {
        const forecasts = dataStore.forecast_12_months;
        const tbody = document.querySelector("#forecast-pipeline-table tbody");
        tbody.innerHTML = "";

        forecasts.forEach(f => {
            const divergence = Math.abs(f.Linear_Regression_Forecast - f.Random_Forest_Forecast);
            
            // Recommendation generation based on trends
            let plan = "Monitor inventory levels.";
            if (f.Random_Forest_Forecast > 90000) {
                plan = "High demand spike: Pre-arrange storage logistics and marketing bundles.";
            } else if (f.Random_Forest_Forecast < f.Linear_Regression_Forecast) {
                plan = "Conservative trend: Focus on customer retention and clearance discounts.";
            } else {
                plan = "Stable growth: Initiate regular promotional cadence.";
            }

            const row = document.createElement("tr");
            row.innerHTML = `
                <td><strong>${f.Month}</strong></td>
                <td>$${f.Linear_Regression_Forecast.toLocaleString('en-US')}</td>
                <td>$${f.Random_Forest_Forecast.toLocaleString('en-US')}</td>
                <td>$${divergence.toLocaleString('en-US', {maximumFractionDigits: 0})}</td>
                <td><i class="fa-solid fa-clipboard-check text-indigo"></i> ${plan}</td>
            `;
            tbody.appendChild(row);
        });
    }

    // -------------------------------------------------------------
    // Smart Advisor Recommendation Engine
    // -------------------------------------------------------------
    function updateSmartAdvisor() {
        const region = advRegion.value;
        const category = advCategory.value;
        
        // Calculate segment-specific performance
        const segmentOrders = transactions.filter(t => t.region === region && t.category === category);
        
        let sales = 0;
        let profit = 0;
        segmentOrders.forEach(t => {
            sales += t.sales;
            profit += t.profit;
        });

        const margin = sales > 0 ? (profit / sales) * 100 : 0;

        // Populate elements
        document.getElementById("diagnostic-target-label").textContent = `Target: ${region} | ${category}`;
        document.getElementById("adv-stat-sales").textContent = `$${sales.toLocaleString('en-US', {maximumFractionDigits: 0})}`;
        document.getElementById("adv-stat-profit").textContent = `$${profit.toLocaleString('en-US', {maximumFractionDigits: 0})}`;
        
        const marginEl = document.getElementById("adv-stat-margin");
        marginEl.textContent = `${margin.toFixed(1)}%`;
        marginEl.className = "val " + (margin >= 15 ? "text-emerald" : (margin >= 0 ? "text-indigo" : "text-pink"));

        // Generate narrative details dynamically
        let diagnosticText = "";
        let operationalText = "";
        let marketingText = "";

        if (category === "Furniture") {
            diagnosticText = `The ${category} category in the ${region} region is currently generating sales of $${sales.toLocaleString('en-US', {maximumFractionDigits: 0})} with a net profit margin of ${margin.toFixed(1)}%. Furniture typically suffers from high distribution overheads and price wars on foundational items like Tables.`;
            
            operationalText = `1. **Freight Restructuring**: Heavy tables and chairs are draining profits. Introduce regional shipping surcharges or partner with local delivery nodes to trim logistics costs by ~15%.\n2. **Inventory Controls**: Restrict stock of tables sold at negative margins; prioritize furnishings and lightweight decor with shorter stocking cycles.`;
            
            marketingText = `1. **High-Margin Cross-Selling**: Attach premium furniture accessories (lamps, cushions, polish kits) during online checkout flows.\n2. **Loyalty Discounts**: Repeat customers contribute over 65% of regional revenue. Offer a 'Home Renewal Package' discount strictly aimed at past buyers to drive higher transaction baskets.`;
        } 
        else if (category === "Electronics") {
            diagnosticText = `The ${category} category in the ${region} region is our high-octane growth engine, delivering $${sales.toLocaleString('en-US', {maximumFractionDigits: 0})} in revenue with a strong profit margin of ${margin.toFixed(1)}%. Customer transaction velocity is concentrated heavily on weekends.`;
            
            operationalText = `1. **Warehouse Allocations**: West and East regions are draining stock quickly. Shift 10-15% of regional warehouse allocations to the highest velocity local hub to prevent stockouts.\n2. **Supplier Negotiation**: Leverage massive sales volume to renegotiate raw bulk costs on smartwatches and phone accessories, aiming to lift margins by 2-3%.`;
            
            marketingText = `1. **Weekend Flash Campaigns**: Our data reveals weekend sales boosts are significant. Launch localized mobile app notifications on Friday afternoons featuring time-sensitive smartwatch bundles.\n2. **Premium Financing Options**: Introduce zero-interest payment installments for high-value laptops during seasonal holiday spikes to boost conversions by up to 22%.`;
        } 
        else { // Office Supplies
            diagnosticText = `The ${category} category in the ${region} region shows outstanding structural health, generating a profit margin of ${margin.toFixed(1)}% on a sales base of $${sales.toLocaleString('en-US', {maximumFractionDigits: 0})}. Office supplies represent stable, high-frequency, low-variance product sales.`;
            
            operationalText = `1. **Automated Procurement**: Integrate automated inventory restocking triggers for high-frequency sub-categories (paper, binders) to reduce storage management cycles.\n2. **Bulk Packing Consolidation**: Encourage multi-pack shipping configurations (e.g. cartons rather than single boxes) to capture bulk freight discounts.`;
            
            marketingText = `1. **Corporate B2B Subscriptions**: Target schools, clinics, and offices with recurring monthly delivery subscriptions (e.g., paper/storage bundles) for a locked-in 10% discount, securing persistent annuity income streams.\n2. **Basket Booster incentives**: Offer a free shipping threshold for orders exceeding $75 to push small transactional accounts into larger shopping values.`;
        }

        document.getElementById("adv-narrative-diagnostic").innerHTML = diagnosticText;
        document.getElementById("adv-narrative-operational").innerHTML = operationalText.replace(/\n/g, "<br>");
        document.getElementById("adv-narrative-marketing").innerHTML = marketingText.replace(/\n/g, "<br>");
    }

    // -------------------------------------------------------------
    // Core Refresh Orchestrator
    // -------------------------------------------------------------
    function updateDashboard() {
        const filtered = getFilteredData();
        
        // Recalculations
        calculateAndDisplayKPIs(filtered);
        
        // Re-render Active Tab Visuals to save resources
        renderSummaryTrends(filtered);
        renderSummaryCategoryPie(filtered);
        renderSalesRegional(filtered);
        renderSalesSubcategories(filtered);
        renderCustomerDays(filtered);
        renderCustomerLoyaltyGauge(filtered);
        renderCustomerLeaderboard(filtered);
    }

    // -------------------------------------------------------------
    // Event Registrations
    // -------------------------------------------------------------
    regionFilter.addEventListener("change", updateDashboard);
    categoryFilter.addEventListener("change", updateDashboard);
    loyaltyFilter.addEventListener("change", updateDashboard);
    
    resetFiltersBtn.addEventListener("click", () => {
        regionFilter.value = "ALL";
        categoryFilter.value = "ALL";
        loyaltyFilter.value = "ALL";
        updateDashboard();
    });

    runDiagnosticsBtn.addEventListener("click", updateSmartAdvisor);

    // -------------------------------------------------------------
    // App Bootstrap Execution
    // -------------------------------------------------------------
    // 1. Initial Dashboard Sync
    updateDashboard();
    
    // 2. Load ML Predictions once
    renderMLForecastChart();
    renderForecastTable();
    
    // 3. Load Smart Advisor initial state
    updateSmartAdvisor();
});
