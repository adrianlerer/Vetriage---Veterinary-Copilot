"""
Clinical Decision Support System for VetrIAge
=============================================

Advanced clinical decision support with:
- Species-specific drug contraindications
- Drug interaction checking
- Clinical alert system
- Evidence-based treatment protocols
- ACVIM guidelines integration

Author: VetrIAge Team
Version: 2.1
License: MIT
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"      # Immediate life-threatening
    HIGH = "high"             # Requires immediate attention
    MEDIUM = "medium"         # Important but not urgent
    LOW = "low"               # Informational
    INFO = "info"             # General information


@dataclass
class ClinicalAlert:
    """Clinical alert with evidence"""
    severity: AlertSeverity
    category: str  # 'drug_interaction', 'contraindication', 'lab_value', 'species_specific'
    message: str
    rationale: str
    recommendations: List[str]
    references: List[str]  # PMIDs
    
    def to_dict(self) -> Dict:
        return {
            'severity': self.severity.value,
            'category': self.category,
            'message': self.message,
            'rationale': self.rationale,
            'recommendations': self.recommendations,
            'references': self.references
        }


class DrugSafetyDatabase:
    """Species-specific drug safety database"""
    
    # CRITICAL: Toxic/Contraindicated drugs by species
    SPECIES_CONTRAINDICATIONS = {
        'cat': {
            'acetaminophen': {
                'severity': AlertSeverity.CRITICAL,
                'reason': 'Acetaminophen is HIGHLY TOXIC to cats due to deficient glucuronidation',
                'effects': 'Methemoglobinemia, Heinz body anemia, hepatotoxicity',
                'action': 'DISCONTINUE IMMEDIATELY. Initiate supportive care.',
                'pmids': ['3511406', '15318908']
            },
            'paracetamol': {  # Same as acetaminophen
                'severity': AlertSeverity.CRITICAL,
                'reason': 'Paracetamol (acetaminophen) is HIGHLY TOXIC to cats',
                'effects': 'Methemoglobinemia, Heinz body anemia, hepatotoxicity',
                'action': 'DISCONTINUE IMMEDIATELY. Initiate supportive care.',
                'pmids': ['3511406', '15318908']
            },
            'aspirin': {
                'severity': AlertSeverity.HIGH,
                'reason': 'Cats have prolonged aspirin half-life (40-45 hours) - high toxicity risk',
                'effects': 'Gastric ulceration, salicylism, metabolic acidosis',
                'action': 'Use only with extreme caution. Maximum 10mg/kg q48-72h',
                'pmids': ['16268071']
            },
            'ibuprofen': {
                'severity': AlertSeverity.CRITICAL,
                'reason': 'NSAIDs highly toxic in cats - renal and GI toxicity',
                'effects': 'Acute kidney injury, gastric ulceration, CNS signs',
                'action': 'AVOID. Use feline-specific NSAIDs only (meloxicam, robenacoxib)',
                'pmids': ['11280397']
            },
            'permethrin': {
                'severity': AlertSeverity.CRITICAL,
                'reason': 'Pyrethroid insecticides cause severe neurotoxicity in cats',
                'effects': 'Tremors, seizures, hyperthermia, death',
                'action': 'NEVER use dog flea products on cats. Emergency treatment required.',
                'pmids': ['11063860']
            },
            'benzyl_alcohol': {
                'severity': AlertSeverity.HIGH,
                'reason': 'Deficient metabolism in cats leads to toxicity',
                'effects': 'CNS depression, metabolic acidosis',
                'action': 'Avoid preservatives containing benzyl alcohol in injectable products',
                'pmids': ['2184361']
            }
        },
        'dog': {
            'xylitol': {
                'severity': AlertSeverity.CRITICAL,
                'reason': 'Xylitol causes profound hypoglycemia and acute liver failure in dogs',
                'effects': 'Hypoglycemia within 30min, acute hepatic necrosis, coagulopathy',
                'action': 'IMMEDIATE EMERGENCY. Induce vomiting if recent, IV dextrose, monitor liver',
                'pmids': ['16882619', '22607596']
            },
            'grapes': {
                'severity': AlertSeverity.CRITICAL,
                'reason': 'Grapes/raisins cause idiosyncratic acute kidney injury in dogs',
                'effects': 'Acute renal failure, vomiting, lethargy',
                'action': 'Induce emesis, aggressive fluid therapy, monitor renal function',
                'pmids': ['11128050']
            },
            'chocolate': {
                'severity': AlertSeverity.HIGH,
                'reason': 'Theobromine and caffeine toxicity (variable by chocolate type)',
                'effects': 'Tachycardia, tremors, seizures, cardiac arrhythmias',
                'action': 'Calculate toxic dose, induce emesis, activated charcoal, supportive care',
                'pmids': ['3318634']
            },
            'ivermectin': {
                'severity': AlertSeverity.HIGH,
                'reason': 'MDR1 gene mutation (Collies, Australian Shepherds) causes sensitivity',
                'effects': 'CNS depression, ataxia, blindness, coma',
                'action': 'MDR1 genetic testing recommended. Avoid high doses in at-risk breeds.',
                'pmids': ['11467958']
            }
        },
        'horse': {
            'corticosteroids': {
                'severity': AlertSeverity.HIGH,
                'reason': 'High risk of laminitis induction, especially in metabolic horses',
                'effects': 'Acute laminitis, hyperglycemia, immunosuppression',
                'action': 'Use with caution. Consider risk factors. Use local/regional when possible.',
                'pmids': ['15771635']
            },
            'trimethoprim_sulfa': {
                'severity': AlertSeverity.MEDIUM,
                'reason': 'Can cause immune-mediated reactions in horses',
                'effects': 'Anemia, thrombocytopenia, anaphylaxis',
                'action': 'Monitor CBC. Discontinue if signs of immune reaction.',
                'pmids': ['3505394']
            }
        },
        'bird': {
            'zinc': {
                'severity': AlertSeverity.CRITICAL,
                'reason': 'Zinc toxicity common from cages, toys, coins',
                'effects': 'Hemolytic anemia, GI signs, hepatotoxicity, renal failure',
                'action': 'Remove source, chelation therapy (EDTA, DMSA), supportive care',
                'pmids': ['8280673']
            },
            'avocado': {
                'severity': AlertSeverity.HIGH,
                'reason': 'Persin toxicity in birds',
                'effects': 'Cardiac necrosis, respiratory distress, death',
                'action': 'Avoid all avocado exposure. Emergency care if ingested.',
                'pmids': ['8480995']
            },
            'teflon': {
                'severity': AlertSeverity.CRITICAL,
                'reason': 'PTFE (Teflon) fumes highly toxic to avian respiratory system',
                'effects': 'Acute respiratory distress, pulmonary edema, death',
                'action': 'Environmental emergency. Immediate fresh air, oxygen, corticosteroids.',
                'pmids': ['7623417']
            }
        }
    }
    
    # Drug-drug interactions (simplified - real system would be much larger)
    DRUG_INTERACTIONS = {
        ('nsaid', 'corticosteroid'): {
            'severity': AlertSeverity.HIGH,
            'interaction': 'Increased risk of GI ulceration and perforation',
            'recommendation': 'Avoid concurrent use. If necessary, use GI protectants (omeprazole, sucralfate)',
            'pmids': ['15363762']
        },
        ('nsaid', 'aspirin'): {
            'severity': AlertSeverity.HIGH,
            'interaction': 'Additive GI and renal toxicity',
            'recommendation': 'Avoid concurrent use',
            'pmids': ['16268071']
        },
        ('ace_inhibitor', 'nsaid'): {
            'severity': AlertSeverity.MEDIUM,
            'interaction': 'Reduced antihypertensive effect, increased renal toxicity risk',
            'recommendation': 'Monitor blood pressure and renal function closely',
            'pmids': ['11280397']
        },
        ('furosemide', 'aminoglycoside'): {
            'severity': AlertSeverity.HIGH,
            'interaction': 'Increased ototoxicity and nephrotoxicity',
            'recommendation': 'Use with caution. Monitor renal function and hearing.',
            'pmids': ['7163567']
        }
    }
    
    @classmethod
    def check_contraindication(cls, drug: str, species: str) -> Optional[Dict]:
        """
        Check if drug is contraindicated for species.
        
        Args:
            drug: Drug name (lowercase)
            species: Species (cat, dog, horse, etc.)
        
        Returns:
            Contraindication info dict or None
        """
        drug_lower = drug.lower().strip()
        species_lower = species.lower().strip()
        
        if species_lower not in cls.SPECIES_CONTRAINDICATIONS:
            return None
        
        species_drugs = cls.SPECIES_CONTRAINDICATIONS[species_lower]
        
        # Check exact match
        if drug_lower in species_drugs:
            return species_drugs[drug_lower]
        
        # Check partial matches (e.g., "acetaminophen tablets" contains "acetaminophen")
        for known_drug in species_drugs:
            if known_drug in drug_lower or drug_lower in known_drug:
                return species_drugs[known_drug]
        
        return None
    
    @classmethod
    def check_interaction(cls, drug1: str, drug2: str) -> Optional[Dict]:
        """
        Check for drug-drug interaction.
        
        Args:
            drug1: First drug (lowercase)
            drug2: Second drug (lowercase)
        
        Returns:
            Interaction info dict or None
        """
        # Normalize drug names to drug classes (simplified)
        key1 = (drug1.lower(), drug2.lower())
        key2 = (drug2.lower(), drug1.lower())
        
        if key1 in cls.DRUG_INTERACTIONS:
            return cls.DRUG_INTERACTIONS[key1]
        elif key2 in cls.DRUG_INTERACTIONS:
            return cls.DRUG_INTERACTIONS[key2]
        
        return None


class ClinicalDecisionSupport:
    """Main clinical decision support system"""
    
    def __init__(self):
        self.drug_db = DrugSafetyDatabase()
    
    def analyze_case(self, case_data: Dict, diagnosis_result: Optional[Dict] = None) -> Dict:
        """
        Comprehensive clinical decision support analysis.
        
        Args:
            case_data: Clinical case dictionary
            diagnosis_result: Optional RAG diagnosis result
        
        Returns:
            Dictionary with alerts, recommendations, and protocols
        """
        alerts = []
        
        # 1. Check critical lab values
        lab_alerts = self._check_critical_labs(case_data.get('labs', {}), case_data.get('species'))
        alerts.extend(lab_alerts)
        
        # 2. Check drug contraindications
        drug_alerts = self._check_drug_safety(
            case_data.get('medications', []),
            case_data.get('species'),
            case_data.get('history', '')
        )
        alerts.extend(drug_alerts)
        
        # 3. Check treatment plan if diagnosis provided
        if diagnosis_result:
            treatment_alerts = self._check_treatment_plan(
                diagnosis_result.get('immediate_actions', []),
                case_data.get('species')
            )
            alerts.extend(treatment_alerts)
        
        # 4. Generate clinical pathways
        pathways = self._get_clinical_pathways(case_data, diagnosis_result)
        
        # 5. Get treatment protocols
        protocols = self._get_treatment_protocols(case_data, diagnosis_result)
        
        return {
            'alerts': [alert.to_dict() for alert in alerts],
            'alert_count': {
                'critical': len([a for a in alerts if a.severity == AlertSeverity.CRITICAL]),
                'high': len([a for a in alerts if a.severity == AlertSeverity.HIGH]),
                'medium': len([a for a in alerts if a.severity == AlertSeverity.MEDIUM]),
                'low': len([a for a in alerts if a.severity == AlertSeverity.LOW]),
            },
            'clinical_pathways': pathways,
            'treatment_protocols': protocols,
            'recommendations': self._generate_recommendations(alerts, case_data)
        }
    
    def _check_critical_labs(self, labs: Dict, species: Optional[str]) -> List[ClinicalAlert]:
        """Check for critically abnormal lab values"""
        alerts = []
        
        # Glucose
        if 'glucose' in labs:
            glucose = labs['glucose']
            if glucose > 600:
                alerts.append(ClinicalAlert(
                    severity=AlertSeverity.CRITICAL,
                    category='lab_value',
                    message=f'Severe hyperglycemia detected: {glucose} mg/dL',
                    rationale='Glucose >600 mg/dL indicates severe decompensation with high risk of DKA/HHS',
                    recommendations=[
                        'Immediate insulin therapy required',
                        'Aggressive fluid resuscitation',
                        'Monitor for DKA (check ketones, blood gas)',
                        'Check electrolytes (especially potassium)',
                        'ICU-level monitoring recommended'
                    ],
                    references=['22647246', '21985142']
                ))
            elif glucose < 40:
                alerts.append(ClinicalAlert(
                    severity=AlertSeverity.CRITICAL,
                    category='lab_value',
                    message=f'Severe hypoglycemia detected: {glucose} mg/dL',
                    rationale='Glucose <40 mg/dL can cause seizures, coma, and death',
                    recommendations=[
                        'IMMEDIATE dextrose bolus IV (0.5-1 g/kg)',
                        'Continuous dextrose infusion (2.5-5%)',
                        'Monitor glucose q1-2h',
                        'Investigate underlying cause (insulinoma, xylitol, sepsis)'
                    ],
                    references=['17672767']
                ))
        
        # BUN/Creatinine (Azotemia)
        if 'BUN' in labs and labs['BUN'] > 100:
            alerts.append(ClinicalAlert(
                severity=AlertSeverity.HIGH,
                category='lab_value',
                message=f'Severe azotemia: BUN {labs["BUN"]} mg/dL',
                rationale='BUN >100 indicates severe kidney dysfunction or dehydration',
                recommendations=[
                    'Assess hydration status',
                    'Rule out urinary obstruction',
                    'Aggressive fluid therapy',
                    'Monitor urine output',
                    'Consider nephrotoxic drug exposure'
                ],
                references=['23679132']
            ))
        
        # Hematocrit (Anemia)
        if 'hematocrit' in labs:
            hct = labs['hematocrit']
            if hct < 15 and species and 'cat' in species.lower():
                alerts.append(ClinicalAlert(
                    severity=AlertSeverity.CRITICAL,
                    category='lab_value',
                    message=f'Severe life-threatening anemia: HCT {hct}%',
                    rationale='HCT <15% in cats indicates life-threatening anemia',
                    recommendations=[
                        'Blood transfusion URGENTLY needed',
                        'Type and crossmatch immediately',
                        'Investigate cause (hemolysis, hemorrhage, bone marrow)',
                        'Supplemental oxygen',
                        'ICU monitoring'
                    ],
                    references=['19912520']
                ))
            elif hct < 20 and species and 'dog' in species.lower():
                alerts.append(ClinicalAlert(
                    severity=AlertSeverity.HIGH,
                    category='lab_value',
                    message=f'Severe anemia: HCT {hct}%',
                    rationale='HCT <20% in dogs may require transfusion',
                    recommendations=[
                        'Consider blood transfusion',
                        'Assess for hemorrhage or hemolysis',
                        'Check reticulocyte count',
                        'Rule out IMHA, blood loss, toxins'
                    ],
                    references=['19912520']
                ))
        
        # WBC (Leukocytosis/Leukopenia)
        if 'WBC' in labs:
            wbc = labs['WBC']
            if wbc > 50:
                alerts.append(ClinicalAlert(
                    severity=AlertSeverity.HIGH,
                    category='lab_value',
                    message=f'Marked leukocytosis: WBC {wbc} K/µL',
                    rationale='WBC >50K suggests severe infection, stress, or leukemia',
                    recommendations=[
                        'Review blood smear for blasts/abnormal cells',
                        'Blood culture if sepsis suspected',
                        'Consider infectious disease panel',
                        'Rule out leukemia/lymphoma'
                    ],
                    references=['15766263']
                ))
            elif wbc < 2:
                alerts.append(ClinicalAlert(
                    severity=AlertSeverity.CRITICAL,
                    category='lab_value',
                    message=f'Severe leukopenia: WBC {wbc} K/µL',
                    rationale='WBC <2K indicates severe immunosuppression - high infection risk',
                    recommendations=[
                        'Reverse isolation',
                        'Broad-spectrum antibiotics',
                        'G-CSF (Neupogen) may be indicated',
                        'Rule out parvovirus (dogs), FeLV (cats), bone marrow disease'
                    ],
                    references=['22192476']
                ))
        
        return alerts
    
    def _check_drug_safety(self, medications: List[str], species: Optional[str], history: str) -> List[ClinicalAlert]:
        """Check for drug contraindications and interactions"""
        alerts = []
        
        if not species:
            return alerts
        
        # Check each medication
        for med in medications:
            contraindication = self.drug_db.check_contraindication(med, species)
            if contraindication:
                alerts.append(ClinicalAlert(
                    severity=contraindication['severity'],
                    category='contraindication',
                    message=f'⚠️ {med.upper()} is contraindicated in {species}',
                    rationale=contraindication['reason'],
                    recommendations=[contraindication['action']],
                    references=contraindication['pmids']
                ))
        
        # Check history for mentions of dangerous substances
        history_lower = history.lower()
        
        # Common toxins mentioned in history
        toxin_checks = {
            'cat': ['tylenol', 'acetaminophen', 'advil', 'ibuprofen', 'aspirin'],
            'dog': ['xylitol', 'chocolate', 'grapes', 'raisins', 'onion', 'garlic'],
            'bird': ['avocado', 'teflon', 'zinc']
        }
        
        if species.lower() in toxin_checks:
            for toxin in toxin_checks[species.lower()]:
                if toxin in history_lower:
                    contraindication = self.drug_db.check_contraindication(toxin, species)
                    if contraindication:
                        alerts.append(ClinicalAlert(
                            severity=contraindication['severity'],
                            category='species_specific',
                            message=f'⚠️ {toxin.upper()} exposure mentioned in history',
                            rationale=contraindication['reason'],
                            recommendations=[contraindication['action']],
                            references=contraindication['pmids']
                        ))
        
        return alerts
    
    def _check_treatment_plan(self, treatments: List[str], species: Optional[str]) -> List[ClinicalAlert]:
        """Check proposed treatments for safety"""
        alerts = []
        
        if not species:
            return alerts
        
        for treatment in treatments:
            treatment_lower = treatment.lower()
            
            # Extract drug names from treatment text
            # Simplified - real system would use NLP
            for word in treatment_lower.split():
                contraindication = self.drug_db.check_contraindication(word, species)
                if contraindication:
                    alerts.append(ClinicalAlert(
                        severity=contraindication['severity'],
                        category='treatment_safety',
                        message=f'Proposed treatment contains contraindicated drug: {word}',
                        rationale=contraindication['reason'],
                        recommendations=[
                            contraindication['action'],
                            'Consider alternative medications'
                        ],
                        references=contraindication['pmids']
                    ))
        
        return alerts
    
    def _get_clinical_pathways(self, case_data: Dict, diagnosis_result: Optional[Dict]) -> List[Dict]:
        """Get evidence-based clinical pathways"""
        pathways = []
        
        # Example pathways (real system would have comprehensive database)
        if diagnosis_result:
            primary_dx = diagnosis_result.get('differential_diagnoses', [{}])[0].get('diagnosis', '')
            
            if 'diabetes' in primary_dx.lower():
                pathways.append({
                    'name': 'Diabetes Mellitus Management Pathway',
                    'steps': [
                        '1. Confirm diagnosis (persistent hyperglycemia, glucosuria, +/- ketonuria)',
                        '2. Stabilize patient (fluids, correct electrolytes, insulin if needed)',
                        '3. Initiate insulin therapy (0.25-0.5 U/kg BID, adjust based on curves)',
                        '4. Monitor (home glucose curves, fructosamine)',
                        '5. Adjust insulin dose based on response',
                        '6. Manage concurrent conditions (pancreatitis, UTI, hyperadrenocorticism)',
                        '7. Long-term monitoring (every 3-6 months)'
                    ],
                    'references': ['22647246', '21985142']
                })
        
        return pathways
    
    def _get_treatment_protocols(self, case_data: Dict, diagnosis_result: Optional[Dict]) -> List[Dict]:
        """Get evidence-based treatment protocols"""
        protocols = []
        
        # Species-specific protocols
        species = case_data.get('species', '').lower()
        
        if species == 'cat' and diagnosis_result:
            primary_dx = diagnosis_result.get('differential_diagnoses', [{}])[0].get('diagnosis', '')
            
            if 'diabetes' in primary_dx.lower():
                protocols.append({
                    'name': 'Feline Diabetes Treatment Protocol',
                    'medication': 'Glargine insulin (Lantus)',
                    'dosing': 'Start 0.25-0.5 U/kg BID',
                    'monitoring': 'Glucose curves q7-14 days initially, then monthly',
                    'dietary': 'Low-carbohydrate diet (<10% calories from carbs)',
                    'goals': 'Glucose 90-250 mg/dL, remission if possible',
                    'references': ['22647246']
                })
        
        return protocols
    
    def _generate_recommendations(self, alerts: List[ClinicalAlert], case_data: Dict) -> List[str]:
        """Generate clinical recommendations based on alerts"""
        recommendations = []
        
        critical_count = len([a for a in alerts if a.severity == AlertSeverity.CRITICAL])
        high_count = len([a for a in alerts if a.severity == AlertSeverity.HIGH])
        
        if critical_count > 0:
            recommendations.append(f'⚠️ URGENT: {critical_count} CRITICAL alert(s) require immediate attention')
            recommendations.append('Stabilize patient and address critical issues before proceeding with diagnostic workup')
        
        if high_count > 0:
            recommendations.append(f'⚠️ {high_count} HIGH priority alert(s) identified')
            recommendations.append('Review all alerts before finalizing treatment plan')
        
        # Species-specific recommendations
        species = case_data.get('species', '').lower()
        if species == 'cat':
            recommendations.append('Reminder: Cats are obligate carnivores - ensure high-protein, low-carb diet')
            recommendations.append('Cats hide illness - monitor closely for subtle changes')
        elif species == 'dog':
            recommendations.append('Reminder: Breed-specific considerations may apply (MDR1 in herding breeds, etc.)')
        
        return recommendations
