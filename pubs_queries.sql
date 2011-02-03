select titles.title, authors.au_id from titles 
  inner join title_author on titles.title_id = title_author.title_id
  inner join authors on authors.au_id = title_author.au_id
  where titles.title like '%Executive%'


