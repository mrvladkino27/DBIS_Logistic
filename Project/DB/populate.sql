INSERT INTO public."Department"(adress) VALUES ("Нивки");
INSERT INTO public."Department"(adress) VALUES ("Бощагівка");
INSERT INTO public."Department"(adress) VALUES ("Русанівка");

INSERT INTO public."Distance"(
	first_dep, second_dep, distance)
	VALUES ("Нивки", "Нивки", 0);
INSERT INTO public."Distance"(
	first_dep, second_dep, distance)
	VALUES ("Нивки", "Борщагівка", 7);
INSERT INTO public."Distance"(
	first_dep, second_dep, distance)
	VALUES ("Нивки", "Русанівка", 19);

INSERT INTO public."Distance"(
	first_dep, second_dep, distance)
	VALUES ("Борщагівка", "Борщагівка", 0);
INSERT INTO public."Distance"(
	first_dep, second_dep, distance)
	VALUES ("Борщагівка", "Русанівка", 21);

INSERT INTO public."Distance"(
	first_dep, second_dep, distance)
	VALUES ("Русанівка", "Русанівка", 0);

INSERT INTO public."User"(
	"e-mail", password, name, department, role)
	VALUES ("admin@admin.com", "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4", "Admin", "Нивки", "WORKER");