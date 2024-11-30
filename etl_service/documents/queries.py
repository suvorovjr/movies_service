from .movie import Movie
from .genre import Genre
from documents.person import Person

queries = {
    Movie: """
            SELECT
                fw.id,
                fw.title,
                fw.description,
                fw.rating as imdb_rating,
                COALESCE (array_agg(DISTINCT g.name),'{}') as genres,
                COALESCE (array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role='director'),'{}') as directors_names,
                COALESCE (array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role='actor'),'{}') as actors_names, 
                COALESCE (array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role='writer'),'{}') as writers_names,  
                COALESCE (
                    json_agg(
                        DISTINCT jsonb_build_object(
                            'id', p.id,
                            'name', p.full_name
                        )
                    ) FILTER (WHERE p.id is not null and pfw.role='director'),
                    '[]'
                ) as directors,

                    COALESCE (
                    json_agg(
                        DISTINCT jsonb_build_object(
                            'id', p.id,
                            'name', p.full_name
                        )
                    ) FILTER (WHERE p.id is not null and pfw.role='actor'),
                    '[]'
                ) as actors,

                    COALESCE (
                    json_agg(
                        DISTINCT jsonb_build_object(
                            'id', p.id,
                            'name', p.full_name
                        )
                    ) FILTER (WHERE p.id is not null and pfw.role='writer'),
                    '[]'
                ) as writers
                ,max(v.last_change_date) last_change_date

                FROM content.film_work fw
                LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
                LEFT JOIN content.person p ON p.id = pfw.person_id
                LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
                LEFT JOIN content.genre g ON g.id = gfw.genre_id
                cross join lateral (values (fw.modified), (pfw.created), (p.modified), (gfw.created), (g.modified)) v(last_change_date)
                GROUP BY fw.id
                having max(v.last_change_date) > %s
                ORDER BY fw.modified
                """,
    Genre: """
            SELECT
                gr.id,
                gr.name
            FROM content.genre AS gr
            WHERE gr.modified > %s
            """,
    Person: """
            SELECT
                p.id,
                p.full_name,
                COALESCE (
                    json_agg(
                        DISTINCT jsonb_build_object(
                            'id', pwf.film_work_id,
                            'roles', roles_array.roles
                        )
                    ),
                    '[]'
                ) as films
            FROM content.person AS p
            LEFT JOIN content.person_film_work pwf ON pwf.person_id = p.id
            LEFT JOIN (
                SELECT
                    film_work_id,
                    array_agg(DISTINCT role) AS roles
                FROM content.person_film_work
                GROUP BY film_work_id
            ) AS roles_array ON roles_array.film_work_id = pwf.film_work_id
            cross join lateral (values (pwf.created), (p.modified)) v(last_change_date)
            GROUP BY p.id
            having max(v.last_change_date) > %s
        """
}
