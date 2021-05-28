# Piattaforma ICT Medgold.

end-point generale: 'https://api.med-gold.eu/'

# API disponibili e come utilizzarle:

# - /dataset/{id}/workflow/{wf}

    Permette di definire l'id di un dataset e un workflow associato allo stesso. 
    In questo momento sono disponibili i seguenti dataset: AgMERRA e ECMWF e per quest'ultimo è disponibile il workflow horta.
    
    Richiesta generica per dataset ecmwf e workflow horta:
        - https://api.med-gold.eu/dataset/ecmwf/workflow/horta?lat={lat}&lng={lng}&vars={[vars]}&years={[years]}&months={[months]}
        
        Dove:
            - lat e lng: latitudine e longitudine della località comprese nell'area geografica [52,-13,29,38]
            - vars: lista di variabili tra le seguenti (a sinistra quella da indicare nell'API)
            {"totprec": "total precipitation",
                "tmin2m": "minimum_2m_temperature_in_the_last_24_hours",
                "10u": "10m_u_component_of_wind",
                "10v": "10m_v_component_of_wind",
                "2d": "2m_dewpoint_temperature",
                "ssrd": "surface_solar_radiation_downwards",
                "tmax2m": "maximum_2m_temperature_in_the_last_24_hours"}
            - years: è possibile indicare il periodo tra il 1982 e il 2018. Si tenga presente che i file del 2017 sono disponibili solo per il mese di Dicembre
            - months: è possibile indicare uno o più mesi tra i seguenti 2,10,11

        Esempio di richiesta API di questo tipo:
            - 'https://api.med-gold.eu/dataset/ecmwf/workflow/horta?lat=38&lng=11&vars=totprec,tmax2m,10v,10u,2d,ssrd&years=2018&months=11'
        
        Restituisce un id che rappresenta l'id specifico della richiesta e che permette di controllare, attraverso un'altra richiesta API a /request (vedi sotto), lo stato della richiesta.

# - /datasets

    Richiesta generica:
        - https://api.med-gold.eu/datasets

    Restituisce la lista di tutti i datasets presenti con relative info.

# - /dataset/{id}/info

    Richiesta generica:
        - https://api.med-gold.eu/dataset/ecmwf/info

    Restituisce le info di uno specifico dataset.

# - /dataset/{id}/wfs

    Richiesta generica:
        - https://api.med-gold.eu/dataset/ecmwf/wfs

    Restituisce tutti i workflows disponibili per uno specifico dataset.

# - /request
        
    Richiesta generica:
        - https://api.med-gold.eu/request?id={id}

    Il parametro id corrisponde all'id della richiesta. 
    Restituisce: lo stato della richiesta e nel caso in cui la stessa fosse 'done', l'url da richiamare per scaricare i file

# - /security/{service}

    Dove service indica il servizio disponibile. Attualmente, l'unico servizio disponibile è dato dalla possibilità di richiedere un token per 
    richiamare l'API dall'esterno della piattaforma (chiamato appunto token).

    Richiesta generica:
        - https://api.med-gold.eu/security/token?username={username}&password={password}
    
    Dove: username e password sono le credenziali fornite al momento della registrazione.
    
    Restituisce un {token} che dovra essere inserito nell'Header della richiesta.
    Es:
        - curl -H "Authorization: {token}" https://api.med-gold.eu/

    Modificare l'end-point generico  https://api.med-gold.eu/ in base alla richiesta che si vuole effettuare.
