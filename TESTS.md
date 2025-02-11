# Test results 🔬
> Tested on Apple Silicon M2, 8gb RAM

- Accuracy: 100% (1 validation error) based on test cases.
- Easyocr take more time ~(x3) to extract text due to image conversion.
- LLM models produce slightly the same results based on the prompt with examples and schema description.

# Examples of output
## Bail 1 ✅
Result:
```bash
Failed files:
• data/Bail 1.pdf: 1 validation error for Leasing
duree_bail
  Value error, La durée du bail doit être de relativedelta(years=+6) au lieu de 5 ans 
```

File processor | LLM | Text extraction time (s) | Data extraction time (s) | Total time (s) |
--- | --- | --- | --- | --- |
`unstructured`| gemini-1.5-pro | 5 | 4 | 9 |
`easyocr`| gemini-1.5-pro | 18 | 4 | 22 |

## Bail 2 ✅
Result:
```json
[
  {
    "bailleur": "Pierre Durand",
    "preneur": "Le Petit Bistrot",
    "adresse": "7 Rue de la Gare, 75012 Paris",
    "description": "salle principale, une réserve, et des sanitaires | usage: restaurant",
    "surface": 100.0,
    "date_prise_effet": {
      "day": 1,
      "month": 4,
      "year": 2025
    },
    "date_fin": {
      "day": 31,
      "month": 3,
      "year": 2031
    },
    "duree_bail": {
      "years": 6,
      "months": 0
    }
  }
]
```

File processor | LLM | Text extraction time (s) | Data extraction time (s) | Total time (s) |
--- | --- | --- | --- | --- |
`unstructured`| gemini-1.5-pro | 4 | 5 | 8 |
`easyocr`| gemini-1.5-pro | 16 | 5 | 21 |

## Bail 3 ✅
Result:
```json
[
  {
    "bailleur": "François Girard",
    "preneur": "Maison du Livre",
    "adresse": "4 Rue de l’Académie, 75009 Paris",
    "description": "une grande salle de vente, un bureau et des sanitaires | usage: librairie",
    "surface": 60.0,
    "date_prise_effet": {
      "day": 1,
      "month": 6,
      "year": 2025
    },
    "date_fin": {
      "day": 31,
      "month": 5,
      "year": 2034
    },
    "duree_bail": {
      "years": 9,
      "months": 0
    }
  }
]
```
File processor | LLM | Text extraction time (s) | Data extraction time (s) | Total time (s) |
--- | --- | --- | --- | --- |
`unstructured`| gemini-1.5-pro | 4 | 4 | 8 |
`easyocr`| gemini-1.5-pro | 18 | 4 | 22 |

## Bail 4 ✅
Result:
```json
[
  {
    "bailleur": "SCI DANET et Filles",
    "preneur": "ZIZARA",
    "adresse": "Rue du Pressoir, 28500 VERNOUILLET",
    "description": "Un local destiné à l’usage de MAGASIN d’une surface de 40m2 avec son parking à l’avant | usage: d’atelier de retouches en confection",
    "surface": 40.0,
    "date_prise_effet": {
      "day": 7,
      "month": 2,
      "year": 2001
    },
    "date_fin": {
      "day": 6,
      "month": 2,
      "year": 2010
    },
    "duree_bail": {
      "years": 9,
      "months": 0
    }
  }
]
```

File processor | LLM | Text extraction time (s) | Data extraction time (s) | Total time (s) |
--- | --- | --- | --- | --- |
`unstructured`| gemini-1.5-pro | 39 | 5 | 44 |
`easyocr`| gemini-1.5-pro | 110 | 5 | 115 |
