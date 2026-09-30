"""Punjab-aligned Grade 7 General Science curriculum seed (prototype scope)."""

CURRICULUM = {
    "version": {
        "name": "PCTB General Science Grade 7 — 2024 Approved",
        "board": "Punjab Curriculum and Textbook Board",
        "year": "2024",
        "status": "approved",
        "notes": "Prototype corpus: one complete textbook subset (5 chapters) demonstrating Grade → Subject → Book → Chapter → Topic → SLO → Concept traceability.",
    },
    "book": {
        "grade": 7,
        "subject": "General Science",
        "title": "General Science for Class VII (PCTB)",
        "language": "en",
        "publisher": "Punjab Curriculum and Textbook Board",
        "source_file": "sample_curriculum/grade7_science_punjab.txt",
    },
    "chapters": [
        {
            "number": 1,
            "title": "Human Organ Systems",
            "difficulty": "medium",
            "page_start": 1,
            "page_end": 22,
            "expected_level": "Grade 7 / Middle",
            "summary": "This chapter introduces the major human organ systems, with emphasis on the digestive, respiratory, circulatory and excretory systems. Students learn how organs work together to keep the body alive, and how healthy habits support these systems.",
            "topics": [
                {
                    "title": "Organisation of the human body",
                    "order": 1,
                    "summary": "Cells form tissues, tissues form organs, and organs work together as organ systems.",
                    "subtopics": [
                        {
                            "title": "From cell to organism",
                            "content": "The human body is organised in levels. A cell is the basic unit of life. Similar cells form a tissue. Different tissues join to form an organ. Organs that work together form an organ system. All organ systems together make the organism.",
                        }
                    ],
                    "slos": [
                        {
                            "code": "SLO-7-SCI-1.1",
                            "statement": "Describe the levels of organisation in the human body from cell to organism.",
                            "bloom": "Understand",
                        },
                        {
                            "code": "SLO-7-SCI-1.2",
                            "statement": "Identify major human organ systems and state the function of each.",
                            "bloom": "Remember",
                        },
                    ],
                    "concepts": [
                        {
                            "name": "Levels of organisation",
                            "explanation": "Life is organised as cell → tissue → organ → organ system → organism. This hierarchy helps us understand how a microscopic cell contributes to the working of the whole body.",
                            "simple_explanation": "Tiny cells join to make tissues. Tissues make organs like the heart. Organs work in teams called systems.",
                            "example": "Muscle cells form muscle tissue; muscle tissue with other tissues forms the heart; the heart belongs to the circulatory system.",
                            "difficulty": "easy",
                            "source_ref": "Ch.1 p.3",
                            "source_excerpt": "A cell is the basic unit of life. Similar cells form a tissue. Different tissues join to form an organ.",
                        },
                        {
                            "name": "Organ system",
                            "explanation": "An organ system is a group of organs that cooperate to perform a major life function such as digestion, transport of blood, or removal of waste.",
                            "simple_explanation": "An organ system is a team of organs that do one big job together.",
                            "example": "The digestive system includes the mouth, oesophagus, stomach, intestines, liver and pancreas.",
                            "difficulty": "easy",
                            "source_ref": "Ch.1 p.4",
                            "source_excerpt": "Organs that work together form an organ system.",
                        },
                    ],
                },
                {
                    "title": "Digestive system",
                    "order": 2,
                    "summary": "Food is broken down mechanically and chemically so nutrients can be absorbed.",
                    "subtopics": [
                        {
                            "title": "Alimentary canal and digestion",
                            "content": "Digestion begins in the mouth where teeth chew food and saliva containing amylase starts breaking starch. The oesophagus pushes food to the stomach by peristalsis. Gastric juice with pepsin and hydrochloric acid digests proteins. The small intestine completes digestion and absorbs nutrients. The large intestine absorbs water and forms faeces.",
                        }
                    ],
                    "slos": [
                        {
                            "code": "SLO-7-SCI-1.3",
                            "statement": "Explain the process of digestion from ingestion to egestion.",
                            "bloom": "Understand",
                        },
                        {
                            "code": "SLO-7-SCI-1.4",
                            "statement": "Relate enzymes to the digestion of carbohydrates, proteins and fats.",
                            "bloom": "Apply",
                        },
                    ],
                    "concepts": [
                        {
                            "name": "Mechanical and chemical digestion",
                            "explanation": "Mechanical digestion is the physical breaking of food into smaller pieces (chewing, churning). Chemical digestion uses enzymes to break large molecules into smaller soluble molecules that can be absorbed.",
                            "simple_explanation": "Teeth mash food. Enzymes are special helpers that cut food into tiny bits the blood can carry.",
                            "example": "Chewing bread is mechanical; salivary amylase turning starch into maltose is chemical.",
                            "difficulty": "medium",
                            "source_ref": "Ch.1 p.7",
                            "source_excerpt": "Digestion begins in the mouth where teeth chew food and saliva containing amylase starts breaking starch.",
                        },
                        {
                            "name": "Enzymes in digestion",
                            "explanation": "Amylase acts on starch, pepsin on proteins in the acidic stomach, and lipase on fats in the small intestine with help of bile from the liver. Enzymes are biological catalysts and work best at specific pH and temperature.",
                            "simple_explanation": "Different enzymes digest different foods: starch, protein or fat.",
                            "example": "If a student eats only boiled rice, amylase is the main enzyme needed at the start of digestion.",
                            "difficulty": "medium",
                            "source_ref": "Ch.1 p.9",
                            "source_excerpt": "Gastric juice with pepsin and hydrochloric acid digests proteins. The small intestine completes digestion and absorbs nutrients.",
                        },
                    ],
                },
                {
                    "title": "Respiratory and circulatory systems",
                    "order": 3,
                    "summary": "Breathing brings oxygen to the blood; the heart pumps blood to all body cells.",
                    "subtopics": [
                        {
                            "title": "Breathing and blood transport",
                            "content": "Air enters through the nose, passes the trachea and bronchi, and reaches alveoli in the lungs. Oxygen diffuses into blood and carbon dioxide diffuses out. The heart has four chambers. Arteries carry blood away from the heart; veins return blood; capillaries allow exchange with tissues.",
                        }
                    ],
                    "slos": [
                        {
                            "code": "SLO-7-SCI-1.5",
                            "statement": "Describe gaseous exchange in the alveoli.",
                            "bloom": "Understand",
                        },
                        {
                            "code": "SLO-7-SCI-1.6",
                            "statement": "Explain how the heart and blood vessels transport materials.",
                            "bloom": "Understand",
                        },
                    ],
                    "concepts": [
                        {
                            "name": "Alveoli and gaseous exchange",
                            "explanation": "Alveoli are tiny air sacs with thin walls and a rich blood supply. Oxygen moves from alveolar air into blood; carbon dioxide moves from blood into alveolar air by diffusion.",
                            "simple_explanation": "Lungs have tiny balloons. Oxygen goes into blood there; waste gas comes out.",
                            "example": "During exercise, breathing rate rises so more oxygen can enter the blood through alveoli.",
                            "difficulty": "medium",
                            "source_ref": "Ch.1 p.14",
                            "source_excerpt": "Oxygen diffuses into blood and carbon dioxide diffuses out.",
                        },
                        {
                            "name": "Double circulation",
                            "explanation": "Human circulation is double: pulmonary circulation takes blood to the lungs and back; systemic circulation takes blood to the body and back. This keeps oxygen-rich and oxygen-poor blood largely separate.",
                            "simple_explanation": "Blood goes to the lungs for oxygen, then to the body, then back to the heart — two loops.",
                            "example": "The right side of the heart sends blood to the lungs; the left side sends blood to the body.",
                            "difficulty": "hard",
                            "source_ref": "Ch.1 p.16",
                            "source_excerpt": "The heart has four chambers. Arteries carry blood away from the heart; veins return blood.",
                        },
                    ],
                },
            ],
            "terms": [
                {"term": "Tissue", "definition": "A group of similar cells performing a common function.", "source_ref": "Ch.1 p.3"},
                {"term": "Peristalsis", "definition": "Wave-like muscle contractions that move food along the alimentary canal.", "source_ref": "Ch.1 p.8"},
                {"term": "Enzyme", "definition": "A biological catalyst that speeds up a chemical reaction in the body.", "source_ref": "Ch.1 p.9"},
                {"term": "Alveoli", "definition": "Tiny air sacs in the lungs where gaseous exchange occurs.", "source_ref": "Ch.1 p.14"},
                {"term": "Artery", "definition": "A blood vessel that carries blood away from the heart.", "source_ref": "Ch.1 p.16"},
                {"term": "Vein", "definition": "A blood vessel that carries blood towards the heart.", "source_ref": "Ch.1 p.16"},
            ],
        },
        {
            "number": 2,
            "title": "Photosynthesis and Nutrition in Plants",
            "difficulty": "medium",
            "page_start": 23,
            "page_end": 44,
            "expected_level": "Grade 7 / Middle",
            "summary": "Green plants make their own food by photosynthesis. This chapter explains autotrophic nutrition, the role of chlorophyll, the equation of photosynthesis, factors affecting the process, and why photosynthesis is essential for life on Earth.",
            "topics": [
                {
                    "title": "Autotrophic and heterotrophic nutrition",
                    "order": 1,
                    "summary": "Plants synthesise food; animals depend on plants or other animals.",
                    "subtopics": [
                        {
                            "title": "Modes of nutrition",
                            "content": "Nutrition is the process of obtaining food. Autotrophs, mainly green plants, make food from carbon dioxide and water using sunlight. Heterotrophs cannot make food and depend on autotrophs. Humans and animals are heterotrophs. Some plants such as fungi (studied as decomposers) and parasitic plants show other modes, but the Grade 7 focus is green plants as producers.",
                        }
                    ],
                    "slos": [
                        {
                            "code": "SLO-7-SCI-2.1",
                            "statement": "Differentiate between autotrophic and heterotrophic nutrition with examples.",
                            "bloom": "Understand",
                        }
                    ],
                    "concepts": [
                        {
                            "name": "Autotrophic nutrition",
                            "explanation": "Autotrophic nutrition is the mode in which an organism synthesises organic food from inorganic raw materials. Green plants are autotrophs because they perform photosynthesis.",
                            "simple_explanation": "Green plants cook their own food using air, water and sunlight.",
                            "example": "A wheat plant in a Punjab field makes glucose in its leaves; a goat cannot do this and must eat plants.",
                            "difficulty": "easy",
                            "source_ref": "Ch.2 p.24",
                            "source_excerpt": "Autotrophs, mainly green plants, make food from carbon dioxide and water using sunlight.",
                        },
                        {
                            "name": "Heterotrophic nutrition",
                            "explanation": "Heterotrophs obtain ready-made organic food. Herbivores eat plants, carnivores eat animals, omnivores eat both. All heterotrophs ultimately depend on autotrophs.",
                            "simple_explanation": "Animals and humans cannot make food, so they eat plants or other animals.",
                            "example": "A student eating roti depends on wheat, which made its food by photosynthesis.",
                            "difficulty": "easy",
                            "source_ref": "Ch.2 p.25",
                            "source_excerpt": "Heterotrophs cannot make food and depend on autotrophs. Humans and animals are heterotrophs.",
                        },
                    ],
                },
                {
                    "title": "The process of photosynthesis",
                    "order": 2,
                    "summary": "Chlorophyll captures light to convert carbon dioxide and water into glucose and oxygen.",
                    "subtopics": [
                        {
                            "title": "Equation, site and products",
                            "content": "Photosynthesis is the process by which green plants prepare glucose from carbon dioxide and water in the presence of sunlight and chlorophyll, releasing oxygen. Word equation: Carbon dioxide + Water → Glucose + Oxygen (in presence of sunlight and chlorophyll). Chemical equation: 6CO2 + 6H2O → C6H12O6 + 6O2. The main site is the chloroplast in mesophyll cells of leaves. Chlorophyll is the green pigment that absorbs light energy. Glucose may be used at once for energy, converted to starch for storage, or used to make cellulose, proteins and oils.",
                        },
                        {
                            "title": "Raw materials and their entry",
                            "content": "Carbon dioxide enters leaves through stomata. Water is absorbed by roots and transported through xylem. Sunlight is captured by chlorophyll. Stomata also allow oxygen to leave the leaf. Guard cells control the opening of stomata.",
                        },
                    ],
                    "slos": [
                        {
                            "code": "SLO-7-SCI-2.2",
                            "statement": "Define photosynthesis and write its word and chemical equations.",
                            "bloom": "Remember",
                        },
                        {
                            "code": "SLO-7-SCI-2.3",
                            "statement": "Explain the role of chlorophyll, stomata, water and sunlight in photosynthesis.",
                            "bloom": "Understand",
                        },
                        {
                            "code": "SLO-7-SCI-2.4",
                            "statement": "Apply the photosynthesis equation to predict products when raw materials change.",
                            "bloom": "Apply",
                        },
                    ],
                    "concepts": [
                        {
                            "name": "Photosynthesis",
                            "explanation": "Photosynthesis is the process by which green plants use sunlight, chlorophyll, carbon dioxide and water to produce glucose and oxygen. It stores light energy as chemical energy in food.",
                            "simple_explanation": "Leaves use sunlight to turn air and water into sugar and oxygen.",
                            "example": "A potted plant kept in sunlight produces starch in its leaves; a plant kept in a dark cupboard does not.",
                            "difficulty": "easy",
                            "source_ref": "Ch.2 p.28",
                            "source_excerpt": "Photosynthesis is the process by which green plants prepare glucose from carbon dioxide and water in the presence of sunlight and chlorophyll, releasing oxygen.",
                        },
                        {
                            "name": "Chlorophyll and chloroplast",
                            "explanation": "Chloroplasts are organelles in green plant cells. They contain chlorophyll, which absorbs mainly blue and red light and reflects green, giving leaves their colour. Without chlorophyll, light energy cannot be captured for photosynthesis.",
                            "simple_explanation": "The green colour in leaves is chlorophyll. It catches sunlight like a solar panel.",
                            "example": "A yellow variegated patch on a leaf lacks chlorophyll and does not make starch.",
                            "difficulty": "medium",
                            "source_ref": "Ch.2 p.29",
                            "source_excerpt": "The main site is the chloroplast in mesophyll cells of leaves. Chlorophyll is the green pigment that absorbs light energy.",
                        },
                        {
                            "name": "Stomata",
                            "explanation": "Stomata are pores, usually on the lower leaf surface, bounded by guard cells. They allow carbon dioxide in and oxygen and water vapour out. If stomata stay closed, photosynthesis slows because CO2 cannot enter.",
                            "simple_explanation": "Tiny doors on a leaf let air in and out.",
                            "example": "On a hot dry afternoon some plants partly close stomata to save water, which can reduce photosynthesis.",
                            "difficulty": "medium",
                            "source_ref": "Ch.2 p.31",
                            "source_excerpt": "Carbon dioxide enters leaves through stomata. Guard cells control the opening of stomata.",
                        },
                        {
                            "name": "Photosynthesis equation",
                            "explanation": "Six molecules of carbon dioxide react with six molecules of water to form one molecule of glucose and six molecules of oxygen, using light energy absorbed by chlorophyll.",
                            "simple_explanation": "Air gas + water + light → sugar + oxygen.",
                            "example": "If a leaf receives no CO2, glucose cannot be formed even if light and water are present.",
                            "difficulty": "medium",
                            "source_ref": "Ch.2 p.28",
                            "source_excerpt": "Chemical equation: 6CO2 + 6H2O → C6H12O6 + 6O2.",
                        },
                    ],
                },
                {
                    "title": "Factors affecting photosynthesis and its importance",
                    "order": 3,
                    "summary": "Light, carbon dioxide, water, temperature and chlorophyll limit the rate; the process feeds ecosystems and produces oxygen.",
                    "subtopics": [
                        {
                            "title": "Limiting factors",
                            "content": "The rate of photosynthesis increases with light intensity up to a point, then levels off. Carbon dioxide concentration, availability of water, suitable temperature and amount of chlorophyll also affect the rate. In Punjab winters, low temperature can slow photosynthesis; on cloudy days light may be limiting.",
                        },
                        {
                            "title": "Why photosynthesis matters",
                            "content": "Photosynthesis is the foundation of food chains. It maintains the oxygen content of air. It reduces carbon dioxide. Fossil fuels originally formed from ancient photosynthetic organisms. Cutting forests therefore affects food, oxygen and climate.",
                        },
                    ],
                    "slos": [
                        {
                            "code": "SLO-7-SCI-2.5",
                            "statement": "Analyse how light, CO2, water and temperature affect the rate of photosynthesis.",
                            "bloom": "Analyze",
                        },
                        {
                            "code": "SLO-7-SCI-2.6",
                            "statement": "Evaluate the importance of photosynthesis for life and the environment.",
                            "bloom": "Evaluate",
                        },
                    ],
                    "concepts": [
                        {
                            "name": "Limiting factors of photosynthesis",
                            "explanation": "A limiting factor is the condition in shortest supply that holds back the rate. At night, light is limiting. In a sealed greenhouse, CO2 may become limiting. Wilted plants lack water.",
                            "simple_explanation": "Photosynthesis needs several things. If one is missing, the plant cannot make food well.",
                            "example": "A healthy green plant in a dark room has chlorophyll and water but almost no photosynthesis because light is missing.",
                            "difficulty": "hard",
                            "source_ref": "Ch.2 p.36",
                            "source_excerpt": "The rate of photosynthesis increases with light intensity up to a point, then levels off.",
                        },
                        {
                            "name": "Importance of photosynthesis",
                            "explanation": "Photosynthesis produces food for nearly all living things and releases oxygen used in respiration. It also helps balance carbon dioxide in the atmosphere.",
                            "simple_explanation": "Plants feed the world and make the oxygen we breathe.",
                            "example": "Without photosynthesis, there would be no grain, fruit, or oxygen-rich air for humans in Punjab or anywhere else.",
                            "difficulty": "easy",
                            "source_ref": "Ch.2 p.38",
                            "source_excerpt": "Photosynthesis is the foundation of food chains. It maintains the oxygen content of air.",
                        },
                    ],
                },
            ],
            "terms": [
                {"term": "Photosynthesis", "definition": "Process by which green plants make glucose from CO2 and water using sunlight and chlorophyll, releasing oxygen.", "source_ref": "Ch.2 p.28"},
                {"term": "Chlorophyll", "definition": "Green pigment in chloroplasts that absorbs light energy for photosynthesis.", "source_ref": "Ch.2 p.29"},
                {"term": "Chloroplast", "definition": "Organelle in green plant cells where photosynthesis occurs.", "source_ref": "Ch.2 p.29"},
                {"term": "Stomata", "definition": "Pores in the leaf epidermis for gas exchange, controlled by guard cells.", "source_ref": "Ch.2 p.31"},
                {"term": "Glucose", "definition": "Simple sugar (C6H12O6) produced during photosynthesis.", "source_ref": "Ch.2 p.28"},
                {"term": "Starch", "definition": "Storage carbohydrate formed from glucose in plants.", "source_ref": "Ch.2 p.30"},
                {"term": "Autotroph", "definition": "Organism that makes its own food from inorganic materials.", "source_ref": "Ch.2 p.24"},
                {"term": "Heterotroph", "definition": "Organism that depends on other organisms for food.", "source_ref": "Ch.2 p.25"},
            ],
        },
        {
            "number": 3,
            "title": "Transport in Plants and Animals",
            "difficulty": "medium",
            "page_start": 45,
            "page_end": 64,
            "expected_level": "Grade 7 / Middle",
            "summary": "Living things must move materials. Plants use xylem and phloem; humans use blood, the heart and vessels. The chapter links plant transport to photosynthesis (water and sugars) and animal transport to respiration and excretion.",
            "topics": [
                {
                    "title": "Transport in plants",
                    "order": 1,
                    "summary": "Xylem carries water and minerals; phloem carries food.",
                    "subtopics": [
                        {
                            "title": "Xylem, phloem and transpiration",
                            "content": "Xylem vessels transport water and dissolved minerals from roots to leaves. Phloem transports sugars from leaves to growing and storage parts (translocation). Transpiration is the loss of water vapour from aerial parts, mainly through stomata. It helps pull the transpiration stream upward and cools the plant.",
                        }
                    ],
                    "slos": [
                        {
                            "code": "SLO-7-SCI-3.1",
                            "statement": "Distinguish between the functions of xylem and phloem.",
                            "bloom": "Understand",
                        },
                        {
                            "code": "SLO-7-SCI-3.2",
                            "statement": "Explain transpiration and its significance.",
                            "bloom": "Understand",
                        },
                    ],
                    "concepts": [
                        {
                            "name": "Xylem",
                            "explanation": "Xylem is a vascular tissue of dead, hollow cells forming tubes. It carries water and mineral salts upward and also provides mechanical support.",
                            "simple_explanation": "Xylem is the plant's water pipe from roots to leaves.",
                            "example": "Wilting occurs when xylem cannot supply enough water to replace water lost by transpiration.",
                            "difficulty": "medium",
                            "source_ref": "Ch.3 p.47",
                            "source_excerpt": "Xylem vessels transport water and dissolved minerals from roots to leaves.",
                        },
                        {
                            "name": "Phloem",
                            "explanation": "Phloem is living vascular tissue that translocates sucrose and other organic substances from sources (leaves) to sinks (roots, fruits, growing tips).",
                            "simple_explanation": "Phloem is the plant's food pipe.",
                            "example": "Sugar made by photosynthesis in a mango leaf travels in phloem to the developing fruit.",
                            "difficulty": "medium",
                            "source_ref": "Ch.3 p.48",
                            "source_excerpt": "Phloem transports sugars from leaves to growing and storage parts (translocation).",
                        },
                        {
                            "name": "Transpiration",
                            "explanation": "Transpiration is evaporation of water from plant surfaces, mainly stomata. It creates a pull that helps water rise, brings minerals up, and cools leaves.",
                            "simple_explanation": "Plants sweat water from leaves. This helps pull more water up from the soil.",
                            "example": "A plastic bag tied around a leafy branch collects water droplets from transpiration.",
                            "difficulty": "medium",
                            "source_ref": "Ch.3 p.50",
                            "source_excerpt": "Transpiration is the loss of water vapour from aerial parts, mainly through stomata.",
                        },
                    ],
                },
                {
                    "title": "Transport in humans",
                    "order": 2,
                    "summary": "Blood is a transport tissue pumped by the heart.",
                    "subtopics": [
                        {
                            "title": "Blood and circulation",
                            "content": "Blood consists of plasma, red blood cells, white blood cells and platelets. Plasma carries nutrients, hormones and wastes. Red cells contain haemoglobin for oxygen. White cells defend against disease. Platelets help clotting. The heart pumps blood through arteries, capillaries and veins.",
                        }
                    ],
                    "slos": [
                        {
                            "code": "SLO-7-SCI-3.3",
                            "statement": "Describe the components of blood and their functions.",
                            "bloom": "Remember",
                        },
                        {
                            "code": "SLO-7-SCI-3.4",
                            "statement": "Relate blood transport to the needs of body cells.",
                            "bloom": "Apply",
                        },
                    ],
                    "concepts": [
                        {
                            "name": "Components of blood",
                            "explanation": "Plasma is the liquid part. Erythrocytes transport oxygen using haemoglobin. Leucocytes fight pathogens. Platelets start clot formation to prevent blood loss.",
                            "simple_explanation": "Blood has a liquid and three kinds of cells: oxygen carriers, germ fighters, and clot makers.",
                            "example": "A cut stops bleeding because platelets help form a clot.",
                            "difficulty": "easy",
                            "source_ref": "Ch.3 p.56",
                            "source_excerpt": "Blood consists of plasma, red blood cells, white blood cells and platelets.",
                        },
                        {
                            "name": "Haemoglobin",
                            "explanation": "Haemoglobin is an iron-containing protein in red blood cells that binds oxygen in the lungs and releases it in tissues.",
                            "simple_explanation": "Haemoglobin is the red pigment that carries oxygen.",
                            "example": "Iron-deficiency anaemia reduces haemoglobin, so a student may feel tired because tissues get less oxygen.",
                            "difficulty": "medium",
                            "source_ref": "Ch.3 p.57",
                            "source_excerpt": "Red cells contain haemoglobin for oxygen.",
                        },
                    ],
                },
            ],
            "terms": [
                {"term": "Xylem", "definition": "Vascular tissue that transports water and minerals from roots to leaves.", "source_ref": "Ch.3 p.47"},
                {"term": "Phloem", "definition": "Vascular tissue that transports food from leaves to other parts.", "source_ref": "Ch.3 p.48"},
                {"term": "Transpiration", "definition": "Loss of water vapour from plant aerial parts, mainly stomata.", "source_ref": "Ch.3 p.50"},
                {"term": "Translocation", "definition": "Transport of organic food in phloem.", "source_ref": "Ch.3 p.48"},
                {"term": "Haemoglobin", "definition": "Iron-containing protein in red blood cells that carries oxygen.", "source_ref": "Ch.3 p.57"},
                {"term": "Plasma", "definition": "Liquid part of blood that carries dissolved substances.", "source_ref": "Ch.3 p.56"},
            ],
        },
        {
            "number": 4,
            "title": "Environment and Feeding Relationships",
            "difficulty": "easy",
            "page_start": 65,
            "page_end": 82,
            "expected_level": "Grade 7 / Middle",
            "summary": "Living things interact with each other and with non-living surroundings. Food chains and webs show how energy from the Sun, captured by photosynthesis, flows through producers, consumers and decomposers. Human activities can disturb these relationships.",
            "topics": [
                {
                    "title": "Ecosystem components",
                    "order": 1,
                    "summary": "Biotic and abiotic factors together make an ecosystem.",
                    "subtopics": [
                        {
                            "title": "Living and non-living factors",
                            "content": "An ecosystem is a community of living organisms interacting with one another and with their physical environment. Biotic factors are living (plants, animals, microbes). Abiotic factors are non-living (light, temperature, water, soil, air). A pond, a wheat field and a forest are ecosystems found in Punjab.",
                        }
                    ],
                    "slos": [
                        {
                            "code": "SLO-7-SCI-4.1",
                            "statement": "Define ecosystem and distinguish biotic and abiotic factors.",
                            "bloom": "Remember",
                        }
                    ],
                    "concepts": [
                        {
                            "name": "Ecosystem",
                            "explanation": "An ecosystem includes all organisms in an area plus the non-living conditions they depend on. Energy flows and materials cycle within it.",
                            "simple_explanation": "An ecosystem is nature's neighbourhood: living things plus air, water, soil and light.",
                            "example": "In a canal ecosystem, fish, plants, insects, water, sunlight and dissolved oxygen all interact.",
                            "difficulty": "easy",
                            "source_ref": "Ch.4 p.66",
                            "source_excerpt": "An ecosystem is a community of living organisms interacting with one another and with their physical environment.",
                        },
                        {
                            "name": "Biotic and abiotic factors",
                            "explanation": "Biotic factors are living components. Abiotic factors are physical and chemical conditions. Both must be suitable for organisms to survive.",
                            "simple_explanation": "Living things and non-living conditions both matter.",
                            "example": "Fish die if abiotic oxygen in water falls, even if food (biotic) is present.",
                            "difficulty": "easy",
                            "source_ref": "Ch.4 p.67",
                            "source_excerpt": "Biotic factors are living. Abiotic factors are non-living (light, temperature, water, soil, air).",
                        },
                    ],
                },
                {
                    "title": "Food chains, webs and energy flow",
                    "order": 2,
                    "summary": "Producers capture solar energy; consumers and decomposers transfer it.",
                    "subtopics": [
                        {
                            "title": "Producers, consumers, decomposers",
                            "content": "Producers (green plants) make food by photosynthesis. Primary consumers are herbivores. Secondary and tertiary consumers are carnivores or omnivores. Decomposers such as bacteria and fungi break down dead matter and recycle nutrients. A food chain is a single pathway; a food web is many linked chains. Only about 10% of energy passes to the next trophic level.",
                        }
                    ],
                    "slos": [
                        {
                            "code": "SLO-7-SCI-4.2",
                            "statement": "Construct food chains and food webs from given organisms.",
                            "bloom": "Apply",
                        },
                        {
                            "code": "SLO-7-SCI-4.3",
                            "statement": "Analyse why energy decreases along a food chain.",
                            "bloom": "Analyze",
                        },
                    ],
                    "concepts": [
                        {
                            "name": "Food chain",
                            "explanation": "A food chain shows who eats whom, starting from a producer. Example: grass → grasshopper → frog → snake. Arrows show the direction of energy flow.",
                            "simple_explanation": "A food chain is a line of who eats whom, starting with a plant.",
                            "example": "Wheat → mouse → owl is a simple chain in a Punjab field.",
                            "difficulty": "easy",
                            "source_ref": "Ch.4 p.72",
                            "source_excerpt": "A food chain is a single pathway; a food web is many linked chains.",
                        },
                        {
                            "name": "Energy flow and 10% rule",
                            "explanation": "Organisms use most energy for life processes and lose some as heat. Roughly one tenth of energy is available to the next trophic level, so food chains are short.",
                            "simple_explanation": "Each eater gets only a little of the energy from the food below it.",
                            "example": "If plants store 1000 units of energy, herbivores may get about 100, and carnivores about 10.",
                            "difficulty": "hard",
                            "source_ref": "Ch.4 p.75",
                            "source_excerpt": "Only about 10% of energy passes to the next trophic level.",
                        },
                        {
                            "name": "Decomposers",
                            "explanation": "Decomposers break down dead organisms and waste, returning minerals to soil so plants can use them again.",
                            "simple_explanation": "Decomposers are nature's recyclers.",
                            "example": "Fallen leaves in a school garden disappear because fungi and bacteria digest them.",
                            "difficulty": "easy",
                            "source_ref": "Ch.4 p.73",
                            "source_excerpt": "Decomposers such as bacteria and fungi break down dead matter and recycle nutrients.",
                        },
                    ],
                },
            ],
            "terms": [
                {"term": "Ecosystem", "definition": "Living community plus its non-living environment, interacting as a unit.", "source_ref": "Ch.4 p.66"},
                {"term": "Producer", "definition": "Organism, usually a green plant, that makes food by photosynthesis.", "source_ref": "Ch.4 p.72"},
                {"term": "Consumer", "definition": "Organism that feeds on other organisms.", "source_ref": "Ch.4 p.72"},
                {"term": "Decomposer", "definition": "Organism that breaks down dead material and recycles nutrients.", "source_ref": "Ch.4 p.73"},
                {"term": "Food web", "definition": "Network of interconnected food chains in an ecosystem.", "source_ref": "Ch.4 p.72"},
                {"term": "Trophic level", "definition": "Position of an organism in a food chain (producer, primary consumer, etc.).", "source_ref": "Ch.4 p.75"},
            ],
        },
        {
            "number": 5,
            "title": "Physical and Chemical Changes",
            "difficulty": "medium",
            "page_start": 83,
            "page_end": 100,
            "expected_level": "Grade 7 / Middle",
            "summary": "Matter can change in physical ways (state, shape, dissolving) or chemical ways (new substances). Students learn to classify changes, recognise signs of a chemical reaction, and connect changes to everyday life in the kitchen, farm and environment. Photosynthesis and digestion are chemical changes met earlier.",
            "topics": [
                {
                    "title": "Physical changes",
                    "order": 1,
                    "summary": "Physical changes do not produce a new substance and are often reversible.",
                    "subtopics": [
                        {
                            "title": "States and mixtures",
                            "content": "Melting ice, boiling water, tearing paper, dissolving salt and magnetising iron are physical changes. The substance remains chemically the same. Many physical changes can be reversed: ice melts and water can freeze again; salt can be recovered by evaporation.",
                        }
                    ],
                    "slos": [
                        {
                            "code": "SLO-7-SCI-5.1",
                            "statement": "Identify physical changes and give reasons using properties of matter.",
                            "bloom": "Understand",
                        }
                    ],
                    "concepts": [
                        {
                            "name": "Physical change",
                            "explanation": "A physical change alters form, state or appearance without forming a new chemical substance. Composition stays the same.",
                            "simple_explanation": "The stuff is still the same stuff, just looking or feeling different.",
                            "example": "Ice cream melting on a summer day in Lahore is a physical change; it is still ice cream (mixture) mainly water and milk solids.",
                            "difficulty": "easy",
                            "source_ref": "Ch.5 p.84",
                            "source_excerpt": "Melting ice, boiling water, tearing paper, dissolving salt and magnetising iron are physical changes.",
                        }
                    ],
                },
                {
                    "title": "Chemical changes",
                    "order": 2,
                    "summary": "Chemical changes produce new substances and often show energy change, gas, colour or precipitate.",
                    "subtopics": [
                        {
                            "title": "Reactions in daily life",
                            "content": "Burning wood, rusting iron, cooking an egg, ripening fruit, photosynthesis and respiration are chemical changes. Signs include colour change, gas bubbles, heat or light, and formation of a precipitate. Chemical changes are usually not easy to reverse. Photosynthesis is a chemical change because carbon dioxide and water become glucose and oxygen.",
                        }
                    ],
                    "slos": [
                        {
                            "code": "SLO-7-SCI-5.2",
                            "statement": "Distinguish chemical changes from physical changes with evidence.",
                            "bloom": "Analyze",
                        },
                        {
                            "code": "SLO-7-SCI-5.3",
                            "statement": "Classify photosynthesis, rusting and melting as physical or chemical and justify.",
                            "bloom": "Evaluate",
                        },
                    ],
                    "concepts": [
                        {
                            "name": "Chemical change",
                            "explanation": "A chemical change, or reaction, produces one or more new substances with different properties. Bonds break and form.",
                            "simple_explanation": "A chemical change makes new stuff that was not there before.",
                            "example": "Rust on a gate is not the same as the original iron; it is a new substance.",
                            "difficulty": "medium",
                            "source_ref": "Ch.5 p.90",
                            "source_excerpt": "Burning wood, rusting iron, cooking an egg, ripening fruit, photosynthesis and respiration are chemical changes.",
                        },
                        {
                            "name": "Photosynthesis as a chemical change",
                            "explanation": "In photosynthesis, CO2 and H2O are converted into C6H12O6 and O2. New substances form, so it is a chemical change, not merely a change of state.",
                            "simple_explanation": "The plant does not just warm water; it builds sugar — a new substance.",
                            "example": "Oxygen bubbles from an aquatic plant in sunlight are evidence of a chemical change.",
                            "difficulty": "medium",
                            "source_ref": "Ch.5 p.92",
                            "source_excerpt": "Photosynthesis is a chemical change because carbon dioxide and water become glucose and oxygen.",
                        },
                        {
                            "name": "Rusting",
                            "explanation": "Rusting is the slow reaction of iron with oxygen and moisture to form hydrated iron oxide. It is a chemical change and is prevented by paint, oil or galvanising.",
                            "simple_explanation": "Iron slowly turns into reddish rust when air and water are present.",
                            "example": "A bicycle left in the rain develops rust on unprotected parts.",
                            "difficulty": "easy",
                            "source_ref": "Ch.5 p.93",
                            "source_excerpt": "Burning wood, rusting iron, cooking an egg... are chemical changes.",
                        },
                    ],
                },
            ],
            "terms": [
                {"term": "Physical change", "definition": "Change in which no new substance is formed.", "source_ref": "Ch.5 p.84"},
                {"term": "Chemical change", "definition": "Change in which one or more new substances are formed.", "source_ref": "Ch.5 p.90"},
                {"term": "Rusting", "definition": "Chemical reaction of iron with oxygen and water to form rust.", "source_ref": "Ch.5 p.93"},
                {"term": "Precipitate", "definition": "Insoluble solid that appears when two solutions react.", "source_ref": "Ch.5 p.91"},
                {"term": "Reversible change", "definition": "Change that can be undone, typical of many physical changes.", "source_ref": "Ch.5 p.85"},
            ],
        },
    ],
}
