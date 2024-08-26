
SELECT t3.Fefco_Teil, t3.ArtNr_Teil, t3.ID_Druck, t3.Druckflaeche, t3.Bogen_Laenge_Brutto, t3.Bogen_Breite_Brutto, t8.Kennung AS Maschine, t1.Ruestzeit_Ist, t1.Ruestzeit_Soll, t1.Laufzeit_Ist, t1.Laufzeit_Soll,
		t1.Zeit_Ist, t1.Zeit_Soll, t3.Werkzeug_Nutzen, t3.Bestell_Nutzen, t1.Menge_Soll, t1.Menge_Ist, t3.Bemerkung, t2.LTermin , t2.KndNr, t4.Suchname, t1.AKNR, t1.TeilNr, t1.SchrittNr, t5.Start, t5.Ende,
		t5.Summe_Minuten, t5.ID_Maschstatus, t6.Maschstatus, t7.Lieferdatum AS Lieferdatum_Rohmaterial, t7.BE_Erledigt
FROM schulte_copy.dbo.tbl_PRODUKTION_FERTIGUNGSSCHRITTE t1 inner join
	 schulte_copy.dbo.tbl_PRODUKTION t2 ON t1.AKNR = t2.AKNr inner join
	 schulte_copy.dbo.tbl_PRODUKTION_TEIL t3 ON t1.AKNR = t3.AKNR inner join
	 schulte_copy.dbo.tbl_KUNDEN t4 on t2.KndNr = t4.KndNr inner join
	 schulte_copy.dbo.tbl_MASCHINE_AK_ZEITEN t5 On t1.AKNR = t5.AKNR AND t1.TEILNR = t5.TEILNR AND t1.ID_MaschNr = t5.MaschNr inner join
	 schulte_copy.dbo.tbl_MASCHINE_STATUS t6 ON t5.ID_Maschstatus = t6.ID_Maschstatus LEFT OUTER JOIN
	 schulte_copy.dbo.tbl_BESTELLUNG_KOPF t7 ON t3.BESTNR = t7.BENR LEFT OUTER JOIN
	 schulte_copy.dbo.tbl_MASCHINENPARAMETER t8 ON t1.ID_MASCHNR = t8.MASCHNR
WHERE SchrittNr <> 0 AND ID_MaschNr <> 1