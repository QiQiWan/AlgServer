## 1 The algorithm for foundation pits

### 1.1 The Algorithm to calculate the deformation of the foundation pit by energy principle

#### Introduction

The algorithm is used to calculation the deformation of the foundation pit, which is based on the energy principle. This algorithm consists of five main parts:

1. Define the details of a foundation pit. For example, the size of the foundation pit, the deeph of the foundation pit, the information of soil layers etc. They are all should be defined clearly before calculating.
2. Define the shape function of the retaining wall of the foundation pit. In this progame,  the shape function is defined as the polynomial equations, a parameter is given to determine the order of a polynomial.
3. Calculate the work by external force. The external force mainly includes the earth pressure at the both sides of the retaining wall. Prof. Chen Yekai's theory describing the relationship between the horizontal deformation of the retaining wall and the earth pressure is used in this program.
4. Calculate the strain energy of the retaining structure. Assume that the Euler-Bernoulli beam model is used to describe the feature of the retaining wall, and Bar model under axial force is used to describe the feature of the horizontal supports.
5. Solve the energy equation by variational principle. The functional variation of the undetermined coefficient is calculated, the undetermined coefficient is solved, and the deformation curve of the retaining pile is obtained.

#### 1.1.2 API Explore

This algorithm consists of two interface:

```http
/foundationpit/StartCalTask

/foundationpit/GetCalResult
```

Interfaces must be called sequentially. The first interface is used to create a calculate task, the json of the foundation pit details should be POST as the input data, and the id of the calculate task will be returned in the form of json.

The form of the input data is shown as:

```json
{
    "LeftWall": {
        "L": 16.4,
        "h": 1,
        "Material": {
            "name": "\\u94a2\\u7b4b\\u6df7\\u51dd\\u571f",
            "gamma": 25,
            "E": 60000000000.0,
            "v": 0.3,
            "G": 23076923076.923077
        },
        "I": 0.08333333333333333,
        "E": 60000000000.0,
        "EI": 5000000000.0,
        "kar": 0.8333333333333334,
        "G": 23076923076.923077,
        "H": 12.4
    },
    "RightWall": {
        "L": 16.4,
        "h": 1,
        "Material": {
            "name": "\\u94a2\\u7b4b\\u6df7\\u51dd\\u571f",
            "gamma": 25,
            "E": 60000000000.0,
            "v": 0.3,
            "G": 23076923076.923077
        },
        "I": 0.08333333333333333,
        "E": 60000000000.0,
        "EI": 5000000000.0,
        "kar": 0.8333333333333334,
        "G": 23076923076.923077,
        "H": 12.4
    },
    "H1": 12.4,
    "H2": 12.4,
    "ExcaveDeepth": {
        "LeftSide": 12.4,
        "RightSide": 12.4
    },
    "SupportCount": 1,
    "Supports": [{
        "Material": {
            "name": "\\u6df7\\u51dd\\u571f\\u652f\\u6491",
            "gamma": 25000.0,
            "E": 1000000000.0,
            "A": 1,
            "EA": 1000000000.0
        },
        "SpaceLength": 46.9,
        "N": null
    }],
    "B": 46.9,
    "D": 1,
    "BoreHole": [{
        "soil": {
            "name": "Mudstone ",
            "gamma": 25900.0,
            "E": 100000000.0,
            "phi": 30,
            "c": 300,
            "varepsilon": 0,
            "varphi": 0,
            "alpha": 0,
            "phid": -1.4156504480240402,
            "K0": 0.5,
            "sandy": true,
            "Ka": 0.33333333333333337,
            "Kp": 3.0000000000000004
        },
        "interval": {
            "top": 0,
            "bottom": 16.4
        }
    }],
    "AverageSoil": {
        "name": "Average soil",
        "gamma": 25900.0,
        "E": 100000000.0,
        "phi": 30.0,
        "c": 300.0,
        "varepsilon": 0.0,
        "varphi": 0.0,
        "alpha": 0.0,
        "phid": 0.5242990776014111,
        "K0": 0.5,
        "sandy": true,
        "Ka": 0.33333333333333337,
        "Kp": 3.0000000000000004
    },
    "ds": [0],
    "Palim": 0.005,
    "Pplim": 0.05,
    "PalimWl": 0.08199999999999999,
    "PplimWl": 0.82,
    "PalimWr": 0.08199999999999999,
    "PplimWr": 0.82,
    "LeftOverLoad": 10000.0,
    "RightOverLoad": 10000.0,
    "LeftStrengthLoad": 30000.0,
    "RightStrengthLoad": 30000.0
}
```

Then, the interface will return a response such as:

```json
HTTP 200 OK
Allow: OPTIONS, POST
Content-Type: application/json
Vary: Accept

{
    "code": 200,
    "msg": "success",
    "data": {
        "TaskID": "1686231699",
        "Status": "Waiting"
    }
}
```

Because the duration of calculating may be very long, so the periodic polling is nessessary to check whether the calculation is complete. The second interface is used to check status and get the result. The id of calculation task should be POST, and a response will be returned.

The json example of input data is shown as:

```json
{"id": "1686223709"}
```

If the calculation hasn't been complete yet, the response returned will be like as:

```json
{
    "status": 1,
    "data": "The results are still being calculated!"
}
```

If the calculation has been complete, the response returned will be like as:

```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "status": 2,
        "data": "{\"ID\": \"1686235619\", \"L1\": 16.4, \"L2\": 16.4, \"wl\": {\"1\": 0.007261198972142058, \"z\": 0.0007291366928263987, \"z**5\": 3.391830006306565e-07, \"z**7\": 2.6098168856058234e-09, \"z**9\": 1.2012494328893391e-12, \"z**6\": -3.9016428548686715e-08, \"z**3\": -7.3210251908097076e-06, \"z**4\": -1.3660348665277657e-06, \"z**8\": -8.916865102046783e-11, \"z**2\": -2.2720705831797327e-06}, \"wr\": {\"1\": 0.007261198972183578, \"z**9\": 1.201245279231031e-12, \"z**7\": 2.6098073087554897e-09, \"z**5\": 3.391815728702834e-07, \"z\": 0.0007291366928228193, \"z**2\": -2.272053747758917e-06, \"z**4\": -1.3660276298592373e-06, \"z**6\": -3.9016272756241985e-08, \"z**8\": -8.916834001726595e-11, \"z**3\": -7.321043444392424e-06}, \"symbol\": \"z\"}"
    }
}
```
