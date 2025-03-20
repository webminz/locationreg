create table locations (
	id serial primary key,
	name varchar(1000) not null,
	latitude float not null,
	longitude float not null,
	unique(name)
);

create table registrations(
	id serial primary key,
	location_id integer not null,
	contact_details varchar(1000) not null,
	foreign key (location_id) references locations(id)
);

insert into locations (name, latitude, longitude) values ('bergen', 60.3911838, 5.3255599);
insert into locations (name, latitude, longitude) values ('oslso', 59.9112197, 10.7330275);
insert into locations (name, latitude, longitude) values ('trondheim', 63.4304427, 10.3952956);
