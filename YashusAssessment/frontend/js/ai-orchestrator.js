// AI Orchestration Layer - Domain Sensing & Adaptive Questioning

class AIOrchestrator {
    constructor() {
        this.context = {
            industry: null,
            geography: null,
            businessSize: null,
            estimatedMaturity: null,
            confidence: 0,
            tone: 'professional',
            painPoints: [],
            missingCapabilities: [],
            agentPriorities: [],
            answers: []
        };
        
        this.dimensionQuestions = this.initializeQuestionBank();
    }
    
    // Initial Domain Sensing from first answer
    async processInitialAnswer(businessDescription) {
        console.log('🧠 AI: Processing initial answer...');
        
        // Simulate NLP processing (would call Groq API in production)
        const analysis = await this.analyzeBusinessDescription(businessDescription);
        
        this.context.industry = analysis.industry;
        this.context.geography = analysis.geography;
        this.context.businessSize = analysis.size;
        this.context.estimatedMaturity = analysis.maturity;
        this.context.confidence = analysis.confidence;
        
        console.log('✓ AI Context:', this.context);
        
        return this.context;
    }
    
    // Simulate NLP Analysis
    async analyzeBusinessDescription(text) {
        // Mock implementation - would use Groq API in production
        const lowercaseText = text.toLowerCase();
        
        // Industry detection
        let industry = 'General Business';
        if (lowercaseText.match(/dental|clinic|doctor|medical|healthcare|hospital/)) {
            industry = 'Healthcare';
        } else if (lowercaseText.match(/saas|software|tech|app|platform|ai/)) {
            industry = 'Technology';
        } else if (lowercaseText.match(/retail|store|shop|ecommerce|online store/)) {
            industry = 'Retail/E-commerce';
        } else if (lowercaseText.match(/agency|marketing|consulting|services/)) {
            industry = 'Professional Services';
        } else if (lowercaseText.match(/manufacturing|factory|production|supplier/)) {
            industry = 'Manufacturing';
        }
        
        // Geography detection
        let geography = 'Global';
        if (lowercaseText.match(/mumbai|bangalore|delhi|india|chennai|hyderabad/)) {
            geography = 'India';
        } else if (lowercaseText.match(/usa|america|us|california|new york/)) {
            geography = 'USA';
        }
        
        // Size detection
        let size = 'Small';
        if (lowercaseText.match(/\d+ locations|multiple offices|enterprise|large/)) {
            size = 'Medium';
        }
        if (lowercaseText.match(/\d+ employees/) && parseInt(lowercaseText.match(/(\d+) employees/)?.[1]) > 50) {
            size = 'Medium';
        }
        
        // Maturity signals
        let maturity = 3.0; // Default mid-range
        let signals = {
            website: lowercaseText.match(/website|online presence/) ? 1 : 0,
            social: lowercaseText.match(/social media|facebook|instagram|linkedin/) ? 1 : 0,
            ads: lowercaseText.match(/ads|advertising|ppc|paid marketing/) ? 1 : 0,
            crm: lowercaseText.match(/crm|salesforce|hubspot|customer data/) ? 1 : 0,
            analytics: lowercaseText.match(/analytics|data|tracking|measurement/) ? 1 : 0
        };
        
        let signalCount = Object.values(signals).reduce((a, b) => a + b, 0);
        
        if (signalCount === 0) {
            maturity = 2.0; // Very traditional
        } else if (signalCount >= 3) {
            maturity = 5.0; // Sophisticated
        } else {
            maturity = 3.0 + signalCount * 0.5;
        }
        
        return {
            industry,
            geography,
            size,
            maturity,
            confidence: 0.75 + (signalCount * 0.05),
            signals
        };
    }
    
    // Generate adaptive questions for each dimension
    getAdaptiveQuestions(dimension) {
        const maturity = this.context.estimatedMaturity || 3.0;
        const questions = this.dimensionQuestions[dimension];
        
        if (!questions) return [];
        
        // Select questions based on maturity level
        if (maturity < 3.0) {
            return questions.basic;
        } else if (maturity < 5.0) {
            return questions.intermediate;
        } else {
            return questions.advanced;
        }
    }
    
    // Adapt tone based on industry and maturity
    adaptTone(text) {
        if (this.context.industry === 'Healthcare') {
            text = text.replace(/customers/g, 'patients');
            text = text.replace(/leads/g, 'patient inquiries');
        }
        
        if (this.context.estimatedMaturity < 3.0) {
            // Simplify jargon
            text = text.replace(/conversion funnel/g, 'customer journey');
            text = text.replace(/attribution/g, 'tracking');
            text = text.replace(/optimization/g, 'improvement');
        }
        
        return text;
    }
    
    // Initialize question bank for all 7 dimensions
    initializeQuestionBank() {
        return {
            strategy: {
                basic: [
                    {
                        text: "Do you have a documented marketing plan?",
                        type: "radio",
                        options: ["No formal plan", "Annual plan", "Quarterly plan", "Detailed 90-day plan"]
                    },
                    {
                        text: "How do you set marketing goals?",
                        type: "radio",
                        options: ["No specific goals", "Revenue-based goals", "Specific metrics (leads, conversions)", "OKRs with KPIs"]
                    },
                    {
                        text: "Who makes marketing decisions?",
                        type: "radio",
                        options: ["Owner/founder", "Marketing manager", "Marketing team", "Data-driven committee"]
                    }
                ],
                intermediate: [
                    {
                        text: "How frequently do you review marketing performance?",
                        type: "radio",
                        options: ["Rarely/never", "Quarterly", "Monthly", "Weekly with dashboards"]
                    },
                    {
                        text: "What's your marketing budget as % of revenue?",
                        type: "radio",
                        options: ["<5%", "5-10%", "10-15%", ">15%"]
                    },
                    {
                        text: "Do you have buyer personas documented?",
                        type: "radio",
                        options: ["No personas", "Basic demographics", "Detailed personas", "Data-driven segments"]
                    }
                ],
                advanced: [
                    {
                        text: "How do you allocate budget across channels?",
                        type: "radio",
                        options: ["Gut feel", "Historical spending", "ROI-based allocation", "ML-optimized portfolio"]
                    },
                    {
                        text: "Do you use marketing mix modeling (MMM)?",
                        type: "radio",
                        options: ["What's MMM?", "Heard of it", "Use attribution tools", "Full econometric modeling"]
                    }
                ]
            },
            technology: {
                basic: [
                    {
                        text: "What marketing tools do you currently use?",
                        type: "checkbox",
                        options: ["Website", "Social media", "Email tool", "CRM", "Analytics", "Ads platform", "None"]
                    },
                    {
                        text: "Do you have a CRM system?",
                        type: "radio",
                        options: ["No CRM", "Spreadsheets", "Basic CRM (Zoho/HubSpot)", "Advanced CRM (Salesforce)"]
                    },
                    {
                        text: "How do you track website visitors?",
                        type: "radio",
                        options: ["Don't track", "Google Analytics (not configured)", "GA4 configured", "GA4 + heatmaps + session recording"]
                    }
                ],
                intermediate: [
                    {
                        text: "Do your marketing tools integrate with each other?",
                        type: "radio",
                        options: ["No integrations", "Some manual imports", "Native integrations", "Full automation with Zapier/API"]
                    },
                    {
                        text: "How clean is your customer data?",
                        type: "radio",
                        options: ["Messy/duplicates", "Somewhat clean", "Regularly cleaned", "Automated data hygiene"]
                    }
                ],
                advanced: [
                    {
                        text: "Do you use a Customer Data Platform (CDP)?",
                        type: "radio",
                        options: ["What's a CDP?", "Considering it", "Implementing", "Fully operational"]
                    },
                    {
                        text: "How mature is your marketing automation?",
                        type: "radio",
                        options: ["Manual campaigns", "Basic email automation", "Multi-channel journeys", "AI-powered personalization"]
                    }
                ]
            },
            content: {
                basic: [
                    {
                        text: "How often do you publish new content?",
                        type: "radio",
                        options: ["Rarely/never", "When we remember", "Monthly", "Weekly or more"]
                    },
                    {
                        text: "Who creates your content?",
                        type: "radio",
                        options: ["Owner/staff", "Freelancers", "In-house team", "Agency + in-house"]
                    },
                    {
                        text: "Do you have a content calendar?",
                        type: "radio",
                        options: ["No planning", "Mental notes", "Spreadsheet", "Dedicated tool (Asana/Trello)"]
                    }
                ],
                intermediate: [
                    {
                        text: "How do you decide what content to create?",
                        type: "radio",
                        options: ["Random ideas", "Competitor analysis", "Keyword research", "Data-driven insights"]
                    },
                    {
                        text: "Do you repurpose content across channels?",
                        type: "radio",
                        options: ["One-off posts", "Sometimes repurpose", "Systematic repurposing", "AI-assisted multi-format"]
                    }
                ],
                advanced: [
                    {
                        text: "Do you use AI for content creation?",
                        type: "radio",
                        options: ["No AI", "Trying ChatGPT", "Regular AI assistance", "Fully automated workflows"]
                    },
                    {
                        text: "How do you measure content performance?",
                        type: "radio",
                        options: ["Likes/shares", "Traffic metrics", "Engagement + conversions", "Full attribution to revenue"]
                    }
                ]
            },
            channels: {
                basic: [
                    {
                        text: "Which marketing channels are you actively using?",
                        type: "checkbox",
                        options: ["Website", "SEO", "Google Ads", "Facebook/Instagram", "LinkedIn", "Email", "YouTube", "None"]
                    },
                    {
                        text: "What's your monthly ad spend?",
                        type: "radio",
                        options: ["₹0 (no ads)", "₹1-25K", "₹25-100K", ">₹100K"]
                    },
                    {
                        text: "How do you get most customers today?",
                        type: "radio",
                        options: ["Word of mouth", "Referrals", "Paid ads", "Organic search"]
                    }
                ],
                intermediate: [
                    {
                        text: "Do you track performance by channel?",
                        type: "radio",
                        options: ["No tracking", "Platform analytics only", "Spreadsheet reports", "Unified dashboard"]
                    },
                    {
                        text: "How do you decide channel budgets?",
                        type: "radio",
                        options: ["Equal split", "What worked before", "ROI-based", "Testing + optimization"]
                    }
                ],
                advanced: [
                    {
                        text: "What attribution model do you use?",
                        type: "radio",
                        options: ["Last-click", "First-click", "Linear/time decay", "Data-driven attribution"]
                    },
                    {
                        text: "How mature is your SEO strategy?",
                        type: "radio",
                        options: ["No SEO", "Basic on-page", "Technical + content SEO", "Enterprise SEO program"]
                    }
                ]
            },
            skills: {
                basic: [
                    {
                        text: "How many people work on marketing?",
                        type: "radio",
                        options: ["Just me", "1-2 people", "3-5 people", "6+ people"]
                    },
                    {
                        text: "Do you have dedicated marketing roles?",
                        type: "radio",
                        options: ["Everyone does everything", "Some specialization", "Defined roles", "Specialized teams"]
                    },
                    {
                        text: "How do you train your marketing team?",
                        type: "radio",
                        options: ["No formal training", "Occasional courses", "Regular upskilling", "Structured learning paths"]
                    }
                ],
                intermediate: [
                    {
                        text: "Do you use agencies or freelancers?",
                        type: "radio",
                        options: ["All in-house", "Some freelancers", "Mix of in-house + agency", "Multiple specialized agencies"]
                    },
                    {
                        text: "How do you hire marketing talent?",
                        type: "radio",
                        options: ["Referrals only", "Job boards", "Recruiters", "Employer brand + talent pipeline"]
                    }
                ],
                advanced: [
                    {
                        text: "Do you have a marketing operations (MOps) role?",
                        type: "radio",
                        options: ["What's MOps?", "Considering it", "Part-time role", "Dedicated MOps team"]
                    },
                    {
                        text: "How data-literate is your marketing team?",
                        type: "radio",
                        options: ["Not very", "Basic analytics", "Comfortable with data", "Data scientists embedded"]
                    }
                ]
            },
            measurement: {
                basic: [
                    {
                        text: "How do you measure marketing success?",
                        type: "radio",
                        options: ["Don't measure", "Likes/followers", "Website traffic", "Leads and conversions"]
                    },
                    {
                        text: "Do you know your customer acquisition cost (CAC)?",
                        type: "radio",
                        options: ["No idea", "Rough estimate", "Track by channel", "Real-time dashboard"]
                    },
                    {
                        text: "How often do you look at analytics?",
                        type: "radio",
                        options: ["Never", "When problems occur", "Weekly", "Daily monitoring"]
                    }
                ],
                intermediate: [
                    {
                        text: "Do you calculate Customer Lifetime Value (LTV)?",
                        type: "radio",
                        options: ["No", "Basic calculation", "By segment", "Predictive LTV models"]
                    },
                    {
                        text: "How do you report marketing ROI?",
                        type: "radio",
                        options: ["Don't report", "Revenue vs spend", "Multi-touch attribution", "Incrementality testing"]
                    }
                ],
                advanced: [
                    {
                        text: "Do you run A/B tests regularly?",
                        type: "radio",
                        options: ["No testing", "Occasional tests", "Regular testing", "Continuous experimentation culture"]
                    },
                    {
                        text: "How sophisticated is your analytics setup?",
                        type: "radio",
                        options: ["Basic GA4", "GA4 + event tracking", "Data warehouse", "Full ML/AI analytics stack"]
                    }
                ]
            },
            cx: {
                basic: [
                    {
                        text: "How do customers first contact you?",
                        type: "checkbox",
                        options: ["Phone", "Email", "Website form", "Chat", "Social media", "Walk-in"]
                    },
                    {
                        text: "Do you have a documented customer journey map?",
                        type: "radio",
                        options: ["No map", "Basic flowchart", "Detailed journey map", "Journey maps per persona"]
                    },
                    {
                        text: "How do you collect customer feedback?",
                        type: "radio",
                        options: ["Don't collect", "Informal feedback", "Surveys", "Systematic NPS/CSAT program"]
                    }
                ],
                intermediate: [
                    {
                        text: "How personalized is your marketing?",
                        type: "radio",
                        options: ["One-size-fits-all", "Basic segmentation", "Behavioral triggers", "1:1 personalization at scale"]
                    },
                    {
                        text: "Do you have a customer retention strategy?",
                        type: "radio",
                        options: ["Reactive support", "Email reminders", "Loyalty program", "Proactive success management"]
                    }
                ],
                advanced: [
                    {
                        text: "Do you use predictive analytics for churn?",
                        type: "radio",
                        options: ["No churn tracking", "Manual monitoring", "Basic churn metrics", "ML-powered churn prediction"]
                    },
                    {
                        text: "How mature is your customer data unification?",
                        type: "radio",
                        options: ["Siloed systems", "Some integrations", "Single customer view", "Real-time 360° profile"]
                    }
                ]
            }
        };
    }
    
    // Update context based on new answers
    updateContext(dimension, answers) {
        this.context.answers.push({ dimension, answers });
        
        // Adjust maturity estimate based on answers
        // (Simplified - real implementation would use ML)
        const avgScore = this.calculateDimensionScore(answers);
        this.context.estimatedMaturity = (this.context.estimatedMaturity + avgScore) / 2;
        this.context.confidence = Math.min(this.context.confidence + 0.1, 0.95);
    }
    
    calculateDimensionScore(answers) {
        // Simplified scoring (0-7 scale)
        let total = 0;
        answers.forEach(answer => {
            if (answer.type === 'radio') {
                const optionIndex = answer.selectedIndex || 0;
                total += (optionIndex * 7) / (answer.options.length - 1);
            }
        });
        return total / answers.length;
    }
}

// Export for use in other modules
window.AIOrchestrator = AIOrchestrator;
window.aiOrchestrator = new AIOrchestrator();
