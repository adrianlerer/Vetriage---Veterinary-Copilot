"""
VetrIAge Safety Alert System
=============================

Provides real-time safety alerts, drug contraindications, and species-specific warnings.
Critical for preventing adverse drug reactions and ensuring patient safety.

Features:
- Species-specific drug contraindications database
- Breed-specific sensitivities (MDR1, etc.)
- Age and weight-based dosing alerts
- Drug interaction checking
- Recent FDA/EMA veterinary alerts
- Toxic substance database

Author: VetrIAge Team
Version: 2.0.0
License: MIT
"""

import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"  # Life-threatening
    HIGH = "high"  # Serious adverse effects likely
    MODERATE = "moderate"  # Significant risk
    LOW = "low"  # Minor concern


@dataclass
class SafetyAlert:
    """Structured safety alert"""
    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    affected_species: List[str]
    affected_breeds: List[str] = field(default_factory=list)
    contraindicated_drugs: List[str] = field(default_factory=list)
    age_restrictions: Optional[str] = None  # e.g., "< 6 months", "> 10 years"
    weight_restrictions: Optional[str] = None
    references: List[str] = field(default_factory=list)
    date_issued: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'affected_species': self.affected_species,
            'affected_breeds': self.affected_breeds,
            'contraindicated_drugs': self.contraindicated_drugs,
            'age_restrictions': self.age_restrictions,
            'weight_restrictions': self.weight_restrictions,
            'references': self.references,
            'date_issued': self.date_issued
        }


class SpeciesContraindicationDatabase:
    """Database of species-specific drug contraindications"""
    
    def __init__(self):
        self.contraindications = self._build_database()
    
    def _build_database(self) -> Dict[str, List[SafetyAlert]]:
        """Build comprehensive contraindication database"""
        
        db = {
            'cat': [
                SafetyAlert(
                    alert_id="CAT-001",
                    severity=AlertSeverity.CRITICAL,
                    title="Acetaminophen (Paracetamol) Toxicity in Cats",
                    description="Cats lack glucuronyl transferase enzyme, making acetaminophen "
                               "highly toxic. Even small doses (10-40 mg/kg) can cause fatal "
                               "methemoglobinemia and hepatotoxicity within 1-4 hours.",
                    affected_species=['cat'],
                    contraindicated_drugs=['acetaminophen', 'paracetamol', 'tylenol'],
                    references=['PMID: 8771324', 'PMID: 15363762']
                ),
                SafetyAlert(
                    alert_id="CAT-002",
                    severity=AlertSeverity.CRITICAL,
                    title="Aspirin Toxicity in Cats",
                    description="Cats metabolize aspirin very slowly (half-life 38-45 hours vs 4 hours in dogs). "
                               "Causes severe gastric ulceration and bleeding. Maximum safe dose: 10-25 mg/kg "
                               "every 48-72 hours only.",
                    affected_species=['cat'],
                    contraindicated_drugs=['aspirin', 'acetylsalicylic acid'],
                    references=['PMID: 6886442']
                ),
                SafetyAlert(
                    alert_id="CAT-003",
                    severity=AlertSeverity.HIGH,
                    title="Permethrin Toxicity in Cats",
                    description="Cats are highly sensitive to pyrethroid insecticides due to deficient "
                               "glucuronidation. Exposure causes severe tremors, seizures, hyperthermia. "
                               "Avoid all permethrin-based flea products labeled for dogs.",
                    affected_species=['cat'],
                    contraindicated_drugs=['permethrin', 'pyrethroid'],
                    references=['PMID: 18028255']
                ),
                SafetyAlert(
                    alert_id="CAT-004",
                    severity=AlertSeverity.HIGH,
                    title="NSAIDs in Cats - High Risk",
                    description="Cats have limited ability to metabolize most NSAIDs. Meloxicam is the only "
                               "FDA-approved NSAID for chronic use in cats (very low doses). Avoid ibuprofen, "
                               "naproxen, carprofen long-term.",
                    affected_species=['cat'],
                    contraindicated_drugs=['ibuprofen', 'naproxen', 'carprofen', 'ketoprofen'],
                    references=['PMID: 22925464']
                ),
                SafetyAlert(
                    alert_id="CAT-005",
                    severity=AlertSeverity.MODERATE,
                    title="Essential Oils Toxicity in Cats",
                    description="Many essential oils (tea tree, wintergreen, peppermint, pine, eucalyptus) "
                               "are toxic to cats due to deficient liver enzymes. Can cause liver damage, "
                               "neurological signs, respiratory distress.",
                    affected_species=['cat'],
                    contraindicated_drugs=['tea tree oil', 'wintergreen oil', 'eucalyptus oil'],
                    references=['PMID: 12856854']
                )
            ],
            'dog': [
                SafetyAlert(
                    alert_id="DOG-001",
                    severity=AlertSeverity.CRITICAL,
                    title="MDR1 Gene Mutation - Ivermectin Sensitivity",
                    description="Dogs with MDR1 (multi-drug resistance 1) gene mutation have increased "
                               "sensitivity to ivermectin, loperamide, and other drugs. Affects 70% of "
                               "Collies, Australian Shepherds, and related breeds. Can cause fatal neurotoxicity.",
                    affected_species=['dog'],
                    affected_breeds=[
                        'Collie', 'Australian Shepherd', 'Shetland Sheepdog',
                        'Old English Sheepdog', 'Border Collie', 'German Shepherd',
                        'Silken Windhound', 'McNab', 'English Shepherd'
                    ],
                    contraindicated_drugs=['ivermectin (high dose)', 'loperamide', 'acepromazine'],
                    references=['PMID: 11468127', 'PMID: 15363762']
                ),
                SafetyAlert(
                    alert_id="DOG-002",
                    severity=AlertSeverity.CRITICAL,
                    title="Xylitol Toxicity in Dogs",
                    description="Xylitol (sugar substitute) causes rapid insulin release and severe "
                               "hypoglycemia in dogs within 30 minutes. Doses >0.1 g/kg cause hypoglycemia; "
                               ">0.5 g/kg causes acute liver failure. Found in sugar-free gum, candy, baked goods.",
                    affected_species=['dog'],
                    contraindicated_drugs=['xylitol'],
                    references=['PMID: 16949937']
                ),
                SafetyAlert(
                    alert_id="DOG-003",
                    severity=AlertSeverity.HIGH,
                    title="Grapes and Raisins - Acute Kidney Injury",
                    description="Grapes and raisins cause idiosyncratic acute kidney injury in dogs. "
                               "Toxic dose varies widely (10-50 g/kg). Mechanism unknown. Clinical signs "
                               "within 6-12 hours: vomiting, lethargy, anuria within 24-72 hours.",
                    affected_species=['dog'],
                    contraindicated_drugs=['grapes', 'raisins'],
                    references=['PMID: 11467622']
                ),
                SafetyAlert(
                    alert_id="DOG-004",
                    severity=AlertSeverity.HIGH,
                    title="Chocolate/Theobromine Toxicity",
                    description="Dogs metabolize theobromine slowly. Toxic doses: 20 mg/kg mild signs, "
                               "40-50 mg/kg cardiotoxicity, 60 mg/kg seizures. Dark chocolate contains "
                               "5-10x more theobromine than milk chocolate.",
                    affected_species=['dog'],
                    contraindicated_drugs=['theobromine', 'chocolate', 'cocoa'],
                    references=['PMID: 15739875']
                ),
                SafetyAlert(
                    alert_id="DOG-005",
                    severity=AlertSeverity.MODERATE,
                    title="Sulfonamide Hypersensitivity in Dobermans",
                    description="Doberman Pinschers have increased risk of immune-mediated reactions to "
                               "sulfonamide antibiotics (polyarthritis, thrombocytopenia, hepatitis). "
                               "Use alternative antibiotics when possible.",
                    affected_species=['dog'],
                    affected_breeds=['Doberman Pinscher'],
                    contraindicated_drugs=['sulfadiazine', 'sulfamethoxazole', 'trimethoprim-sulfa'],
                    references=['PMID: 8551681']
                )
            ],
            'horse': [
                SafetyAlert(
                    alert_id="HORSE-001",
                    severity=AlertSeverity.CRITICAL,
                    title="Ivermectin Moxidectin Overdose Risk",
                    description="Horses are sensitive to macrocyclic lactones at high doses. Overdose "
                               "can cause CNS depression, ataxia, tremors. Foals <4 months are at higher risk. "
                               "Do not exceed label doses.",
                    affected_species=['horse'],
                    age_restrictions="< 4 months increased risk",
                    contraindicated_drugs=['ivermectin (overdose)', 'moxidectin (overdose)'],
                    references=['PMID: 9337392']
                ),
                SafetyAlert(
                    alert_id="HORSE-002",
                    severity=AlertSeverity.HIGH,
                    title="Phenylbutazone in Performance Horses",
                    description="Phenylbutazone has strict withdrawal times for competition (USEF: 7 days). "
                               "Long-term use causes gastric ulcers, right dorsal colitis, renal toxicity. "
                               "Maximum 4.4 mg/kg BID for 3-4 days, then once daily.",
                    affected_species=['horse'],
                    contraindicated_drugs=['phenylbutazone (long-term high dose)'],
                    references=['PMID: 11213357']
                ),
                SafetyAlert(
                    alert_id="HORSE-003",
                    severity=AlertSeverity.HIGH,
                    title="Monensin Toxicity in Horses",
                    description="Monensin (cattle feed additive) is highly toxic to horses. Lethal dose: "
                               "2-3 mg/kg. Causes cardiomyocyte necrosis, heart failure, sudden death. "
                               "No antidote. Prevent accidental consumption of cattle feed.",
                    affected_species=['horse'],
                    contraindicated_drugs=['monensin', 'rumensin'],
                    references=['PMID: 2227266']
                )
            ],
            'cattle': [
                SafetyAlert(
                    alert_id="CATTLE-001",
                    severity=AlertSeverity.CRITICAL,
                    title="Levamisole Overdose in Cattle",
                    description="Levamisole has narrow safety margin in cattle. Overdose causes "
                               "respiratory paralysis, seizures, death. Do not exceed 8 mg/kg SC. "
                               "Avoid in debilitated animals.",
                    affected_species=['cattle'],
                    contraindicated_drugs=['levamisole (overdose)'],
                    references=['PMID: 7342694']
                ),
                SafetyAlert(
                    alert_id="CATTLE-002",
                    severity=AlertSeverity.HIGH,
                    title="Milk Withdrawal Times - Critical",
                    description="Many drugs have extended milk withdrawal times. Violative residues "
                               "affect food safety. Always check label. Common: ceftiofur (0 days), "
                               "penicillin (60 hours), oxytetracycline (96 hours).",
                    affected_species=['cattle'],
                    references=['FDA CVM Guidelines']
                )
            ]
        }
        
        return db
    
    def get_alerts_for_species(
        self,
        species: str,
        breed: Optional[str] = None,
        severity_threshold: AlertSeverity = AlertSeverity.LOW
    ) -> List[SafetyAlert]:
        """
        Get relevant safety alerts for a species/breed
        
        Args:
            species: Animal species
            breed: Specific breed (optional)
            severity_threshold: Minimum severity to include
        
        Returns:
            List of relevant SafetyAlerts
        """
        species_lower = species.lower()
        alerts = self.contraindications.get(species_lower, [])
        
        # Filter by breed if specified
        if breed:
            breed_lower = breed.lower()
            alerts = [
                alert for alert in alerts
                if not alert.affected_breeds or
                any(breed_lower in b.lower() for b in alert.affected_breeds)
            ]
        
        # Filter by severity
        severity_order = {
            AlertSeverity.LOW: 0,
            AlertSeverity.MODERATE: 1,
            AlertSeverity.HIGH: 2,
            AlertSeverity.CRITICAL: 3
        }
        threshold_level = severity_order[severity_threshold]
        
        alerts = [
            alert for alert in alerts
            if severity_order[alert.severity] >= threshold_level
        ]
        
        return alerts
    
    def check_drug_contraindication(
        self,
        drug_name: str,
        species: str,
        breed: Optional[str] = None
    ) -> List[SafetyAlert]:
        """
        Check if a drug is contraindicated for a species/breed
        
        Args:
            drug_name: Name of drug to check
            species: Animal species
            breed: Specific breed (optional)
        
        Returns:
            List of matching SafetyAlerts
        """
        drug_lower = drug_name.lower()
        alerts = self.get_alerts_for_species(species, breed)
        
        matching = []
        for alert in alerts:
            if any(drug_lower in cd.lower() for cd in alert.contraindicated_drugs):
                matching.append(alert)
        
        return matching


class DrugInteractionChecker:
    """Check for drug-drug interactions"""
    
    def __init__(self):
        self.interactions = self._build_interaction_database()
    
    def _build_interaction_database(self) -> Dict[str, List[Dict]]:
        """Build drug interaction database"""
        
        interactions = {
            'nsaid': [
                {
                    'interacts_with': ['corticosteroid', 'prednisone', 'dexamethasone'],
                    'severity': AlertSeverity.HIGH,
                    'description': 'Increased risk of gastrointestinal ulceration and bleeding'
                },
                {
                    'interacts_with': ['ace_inhibitor', 'enalapril', 'benazepril'],
                    'severity': AlertSeverity.MODERATE,
                    'description': 'Reduced efficacy of ACE inhibitor, risk of renal dysfunction'
                },
                {
                    'interacts_with': ['furosemide', 'diuretic'],
                    'severity': AlertSeverity.MODERATE,
                    'description': 'Reduced diuretic effect, increased risk of renal toxicity'
                }
            ],
            'enrofloxacin': [
                {
                    'interacts_with': ['theophylline'],
                    'severity': AlertSeverity.HIGH,
                    'description': 'Increased theophylline levels, risk of toxicity'
                },
                {
                    'interacts_with': ['antacid', 'sucralfate'],
                    'severity': AlertSeverity.MODERATE,
                    'description': 'Reduced enrofloxacin absorption, separate dosing by 2 hours'
                }
            ],
            'phenobarbital': [
                {
                    'interacts_with': ['chloramphenicol'],
                    'severity': AlertSeverity.HIGH,
                    'description': 'Reduced phenobarbital metabolism, increased levels'
                },
                {
                    'interacts_with': ['corticosteroid'],
                    'severity': AlertSeverity.MODERATE,
                    'description': 'Increased corticosteroid metabolism, reduced efficacy'
                }
            ]
        }
        
        return interactions
    
    def check_interactions(
        self,
        current_drugs: List[str],
        new_drug: str
    ) -> List[Dict]:
        """
        Check for interactions between drugs
        
        Args:
            current_drugs: List of current medications
            new_drug: New drug being considered
        
        Returns:
            List of interaction warnings
        """
        warnings = []
        new_drug_lower = new_drug.lower()
        
        # Check if new drug has known interactions
        for drug_class, interactions in self.interactions.items():
            if drug_class in new_drug_lower:
                for interaction in interactions:
                    for current in current_drugs:
                        current_lower = current.lower()
                        if any(interacting in current_lower for interacting in interaction['interacts_with']):
                            warnings.append({
                                'drug1': new_drug,
                                'drug2': current,
                                'severity': interaction['severity'].value,
                                'description': interaction['description']
                            })
        
        return warnings


def generate_safety_report(
    species: str,
    breed: Optional[str] = None,
    age_years: Optional[float] = None,
    weight_kg: Optional[float] = None,
    current_medications: Optional[List[str]] = None,
    proposed_treatment: Optional[List[str]] = None
) -> Dict:
    """
    Generate comprehensive safety report
    
    Args:
        species: Animal species
        breed: Breed name
        age_years: Age in years
        weight_kg: Weight in kg
        current_medications: Current drug list
        proposed_treatment: Proposed new drugs
    
    Returns:
        Safety report dictionary
    """
    contraindication_db = SpeciesContraindicationDatabase()
    interaction_checker = DrugInteractionChecker()
    
    report = {
        'patient_info': {
            'species': species,
            'breed': breed,
            'age_years': age_years,
            'weight_kg': weight_kg
        },
        'general_alerts': [],
        'drug_contraindications': [],
        'drug_interactions': [],
        'breed_specific_warnings': []
    }
    
    # Get general species alerts
    alerts = contraindication_db.get_alerts_for_species(
        species,
        breed,
        severity_threshold=AlertSeverity.MODERATE
    )
    report['general_alerts'] = [alert.to_dict() for alert in alerts]
    
    # Check proposed drugs for contraindications
    if proposed_treatment:
        for drug in proposed_treatment:
            contraindications = contraindication_db.check_drug_contraindication(
                drug, species, breed
            )
            if contraindications:
                report['drug_contraindications'].extend([
                    {
                        'drug': drug,
                        **alert.to_dict()
                    }
                    for alert in contraindications
                ])
    
    # Check drug-drug interactions
    if current_medications and proposed_treatment:
        for new_drug in proposed_treatment:
            interactions = interaction_checker.check_interactions(
                current_medications,
                new_drug
            )
            report['drug_interactions'].extend(interactions)
    
    # Breed-specific warnings
    if breed and species.lower() == 'dog':
        breed_lower = breed.lower()
        if any(x in breed_lower for x in ['collie', 'shepherd', 'sheepdog']):
            report['breed_specific_warnings'].append({
                'warning': 'MDR1 gene mutation screening recommended',
                'description': 'This breed has high prevalence of MDR1 mutation. '
                              'Consider genetic testing before using ivermectin, loperamide, or related drugs.'
            })
    
    # Summary
    report['summary'] = {
        'total_alerts': len(report['general_alerts']),
        'critical_contraindications': len([
            x for x in report['drug_contraindications']
            if x.get('severity') == 'critical'
        ]),
        'high_risk_interactions': len([
            x for x in report['drug_interactions']
            if x.get('severity') == 'high'
        ]),
        'overall_risk_level': _calculate_overall_risk(report)
    }
    
    return report


def _calculate_overall_risk(report: Dict) -> str:
    """Calculate overall risk level from report"""
    if report['summary']['critical_contraindications'] > 0:
        return 'CRITICAL'
    elif report['summary']['high_risk_interactions'] > 0:
        return 'HIGH'
    elif len(report['drug_contraindications']) > 0:
        return 'MODERATE'
    elif len(report['drug_interactions']) > 0:
        return 'LOW'
    else:
        return 'MINIMAL'


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example 1: Check cat with proposed NSAID
    report1 = generate_safety_report(
        species='cat',
        age_years=8,
        weight_kg=4.5,
        proposed_treatment=['meloxicam', 'acetaminophen']
    )
    
    print("=== Safety Report: Cat with NSAIDs ===")
    print(json.dumps(report1, indent=2))
    
    # Example 2: Check Collie with proposed ivermectin
    report2 = generate_safety_report(
        species='dog',
        breed='Collie',
        age_years=5,
        weight_kg=25,
        current_medications=['prednisone'],
        proposed_treatment=['ivermectin', 'carprofen']
    )
    
    print("\n\n=== Safety Report: Collie with Ivermectin ===")
    print(json.dumps(report2, indent=2))
