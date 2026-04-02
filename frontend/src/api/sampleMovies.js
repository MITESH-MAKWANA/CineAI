/**
 * sampleMovies.js
 * Static fallback movie data for when TMDB API is unreachable.
 * Contains 120 real movies across all major genres.
 */

export const SAMPLE_MOVIES = [
  // ── Trending ─────────────────────────────────────────────────────────────────
  { id: 550, title: 'Fight Club', poster_path: '/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg', vote_average: 8.4, release_date: '1999-10-15', genre_ids: [18, 53] },
  { id: 680, title: 'Pulp Fiction', poster_path: '/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg', vote_average: 8.5, release_date: '1994-09-10', genre_ids: [53, 80] },
  { id: 13, title: 'Forrest Gump', poster_path: '/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg', vote_average: 8.5, release_date: '1994-07-06', genre_ids: [18, 35] },
  { id: 278, title: 'The Shawshank Redemption', poster_path: '/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg', vote_average: 8.7, release_date: '1994-09-23', genre_ids: [18] },
  { id: 238, title: 'The Godfather', poster_path: '/3bhkrj58Vtu7enYsLLeWorktpsG.jpg', vote_average: 8.7, release_date: '1972-03-14', genre_ids: [18, 80] },
  { id: 27205, title: 'Inception', poster_path: '/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg', vote_average: 8.4, release_date: '2010-07-16', genre_ids: [28, 878, 53] },
  { id: 155, title: 'The Dark Knight', poster_path: '/qJ2tW6WMUDux911r6m7haRef0WH.jpg', vote_average: 9.0, release_date: '2008-07-16', genre_ids: [28, 80, 18] },
  { id: 11, title: 'Star Wars', poster_path: '/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg', vote_average: 8.2, release_date: '1977-05-25', genre_ids: [28, 12, 878] },
  { id: 19404, title: 'Dilwale Dulhania Le Jayenge', poster_path: '/2CAL2433ZeIihfX1Hb2139CX0pW.jpg', vote_average: 8.7, release_date: '1995-10-19', genre_ids: [35, 18, 10749] },
  { id: 14160, title: 'Up', poster_path: '/opi9v0NemSF4kRUzGJVy9HhO9cO.jpg', vote_average: 8.3, release_date: '2009-05-29', genre_ids: [16, 12, 10751] },
  { id: 76341, title: 'Mad Max: Fury Road', poster_path: '/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg', vote_average: 7.8, release_date: '2015-05-13', genre_ids: [28, 12, 878] },
  { id: 299536, title: 'Avengers: Infinity War', poster_path: '/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg', vote_average: 8.3, release_date: '2018-04-25', genre_ids: [28, 12, 878] },
  { id: 24428, title: 'The Avengers', poster_path: '/RYMX2wcKCBAr24UyPD7KE3Xobrj.jpg', vote_average: 7.7, release_date: '2012-04-25', genre_ids: [28, 12, 878] },
  { id: 603, title: 'The Matrix', poster_path: '/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg', vote_average: 8.2, release_date: '1999-03-30', genre_ids: [28, 878] },
  { id: 289, title: 'Casablanca', poster_path: '/5K7cOHoay2mZusSLezBOY0Qxh8a.jpg', vote_average: 8.2, release_date: '1942-11-26', genre_ids: [18, 10749] },
  { id: 389, title: 'Twelve Angry Men', poster_path: '/ow3wq89wM8qd5X7hWKxiRfsFf9C.jpg', vote_average: 8.5, release_date: '1957-04-10', genre_ids: [18] },
  { id: 424, title: "Schindler's List", poster_path: '/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg', vote_average: 8.6, release_date: '1993-11-30', genre_ids: [18, 36, 10752] },
  { id: 129, title: 'Spirited Away', poster_path: '/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg', vote_average: 8.5, release_date: '2001-07-20', genre_ids: [16, 12, 14] },
  { id: 120, title: 'The Lord of the Rings: The Fellowship of the Ring', poster_path: '/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg', vote_average: 8.4, release_date: '2001-12-19', genre_ids: [12, 14, 28] },
  { id: 122, title: 'The Lord of the Rings: The Return of the King', poster_path: '/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg', vote_average: 8.5, release_date: '2003-12-01', genre_ids: [12, 14, 28] },

  // ── Top Rated ─────────────────────────────────────────────────────────────────
  { id: 372058, title: 'Your Name', poster_path: '/q719jXXEzOoYaps6babgKnONONX.jpg', vote_average: 8.5, release_date: '2016-08-26', genre_ids: [16, 10749, 18] },
  { id: 194662, title: 'Birdman', poster_path: '/vSNFBMCBQNUcKENF1nE3k2NxXp2.jpg', vote_average: 7.8, release_date: '2014-08-27', genre_ids: [18, 35] },
  { id: 244786, title: 'Whiplash', poster_path: '/7fn624j5lj3xTme2SgiLCeuedmO.jpg', vote_average: 8.5, release_date: '2014-10-10', genre_ids: [18, 10402] },
  { id: 761053, title: 'Gabriel\'s Inferno', poster_path: '/oyG9TL7FcRP4EZ9Vid6uKzwdndz.jpg', vote_average: 8.7, release_date: '2020-05-29', genre_ids: [10749, 18] },
  { id: 346648, title: 'Paddington 2', poster_path: '/iDvf45gTXBXhJzGM9BimJYGpAZX.jpg', vote_average: 7.8, release_date: '2017-11-10', genre_ids: [35, 12, 10751] },
  { id: 539, title: 'Psycho', poster_path: '/yz4QVqPx3h1hD1DfqqQkCq3rmxW.jpg', vote_average: 8.2, release_date: '1960-09-08', genre_ids: [18, 27, 53] },
  { id: 769, title: 'Goodfellas', poster_path: '/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg', vote_average: 8.5, release_date: '1990-09-12', genre_ids: [18, 80] },
  { id: 197, title: 'Braveheart', poster_path: '/or1gBugydmjToAEq7OZY0owwFk.jpg', vote_average: 7.9, release_date: '1995-05-24', genre_ids: [28, 18, 36, 10752] },
  { id: 497, title: 'The Green Mile', poster_path: '/velWPhVMQeQKcxggNEU8YmU1xZa.jpg', vote_average: 8.5, release_date: '1999-12-10', genre_ids: [18] },
  { id: 637, title: 'Life Is Beautiful', poster_path: '/74hLDKjD5aGYOotO6esUVaeISa2.jpg', vote_average: 8.5, release_date: '1998-12-20', genre_ids: [35, 18, 10749] },

  // ── Popular ────────────────────────────────────────────────────────────────────
  { id: 502356, title: 'The Super Mario Bros. Movie', poster_path: '/qNBAXBIQlnOThrVvA6mA2B5ggV6.jpg', vote_average: 7.1, release_date: '2023-04-05', genre_ids: [16, 12, 10751] },
  { id: 385687, title: 'Fast X', poster_path: '/fiVW06jE7z9F3FaNBaVZoowvQ6x.jpg', vote_average: 7.1, release_date: '2023-05-17', genre_ids: [28, 12, 80] },
  { id: 298618, title: 'The Flash', poster_path: '/rktDFPbfHfUbArZ6OOOKsXcv0Bm.jpg', vote_average: 6.8, release_date: '2023-06-14', genre_ids: [28, 12, 878] },
  { id: 447277, title: 'The Little Mermaid', poster_path: '/ym1dxyOk4jFcSl4Q2zmRrA5BEEN.jpg', vote_average: 6.8, release_date: '2023-05-24', genre_ids: [14, 10749, 10751, 16] },
  { id: 758323, title: 'The Pope\'s Exorcist', poster_path: '/9JBEPLTPSm0d1mbEcLxULjJq9Eh.jpg', vote_average: 6.9, release_date: '2023-04-05', genre_ids: [27, 53] },
  { id: 569094, title: 'Spider-Man: Across the Spider-Verse', poster_path: '/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg', vote_average: 8.7, release_date: '2023-05-31', genre_ids: [16, 28, 12, 878] },
  { id: 346698, title: 'Barbie', poster_path: '/iuFNMS8vlzmfa k3KvLVm6EhZXrk.jpg', vote_average: 7.1, release_date: '2023-07-19', genre_ids: [35, 12, 14] },
  { id: 872585, title: 'Oppenheimer', poster_path: '/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg', vote_average: 8.3, release_date: '2023-07-19', genre_ids: [18, 36] },
  { id: 667538, title: 'Transformers: Rise of the Beasts', poster_path: '/gPbM0MK8CP8A174rmUwGsADNYKD.jpg', vote_average: 6.9, release_date: '2023-06-06', genre_ids: [28, 12, 878] },
  { id: 545611, title: 'Everything Everywhere All at Once', poster_path: '/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg', vote_average: 7.9, release_date: '2022-03-11', genre_ids: [28, 35, 18] },

  // ── Upcoming ───────────────────────────────────────────────────────────────────
  { id: 748783, title: 'The Garfield Movie', poster_path: '/xYduFGuch84jFo6Ws3O6AvVHwDd.jpg', vote_average: 7.0, release_date: '2024-05-24', genre_ids: [16, 35, 12, 10751] },
  { id: 1022789, title: 'Inside Out 2', poster_path: '/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg', vote_average: 7.5, release_date: '2024-06-14', genre_ids: [16, 12, 35] },
  { id: 519182, title: 'Despicable Me 4', poster_path: '/wWba3TaojhK7NdycyUPlh1171Eu.jpg', vote_average: 6.6, release_date: '2024-07-03', genre_ids: [16, 35, 10751] },
  { id: 786892, title: 'Furiosa: A Mad Max Saga', poster_path: '/iADOJ8Zymht2JPMoy3R7xceZprc.jpg', vote_average: 7.7, release_date: '2024-05-22', genre_ids: [28, 12, 878] },
  { id: 823464, title: 'Godzilla x Kong: The New Empire', poster_path: '/z1p34vh7dEOnLDmyCrlUVLuoDef.jpg', vote_average: 6.8, release_date: '2024-03-27', genre_ids: [28, 878, 12] },
  { id: 573435, title: 'Bad Boys: Ride or Die', poster_path: '/oGythE98MYleE6mZlGs5oBGkux1.jpg', vote_average: 7.3, release_date: '2024-06-07', genre_ids: [28, 35, 80] },
  { id: 1011985, title: 'Kung Fu Panda 4', poster_path: '/kDp1vUBnMpe8ak4rjgl3cLELqjU.jpg', vote_average: 6.9, release_date: '2024-03-08', genre_ids: [16, 28, 12, 35, 10751] },
  { id: 1209290, title: 'Civil War', poster_path: '/sh7Rg8Er3tFcN9BpKIPOMvALgZd.jpg', vote_average: 7.1, release_date: '2024-04-12', genre_ids: [28, 18, 53] },
  { id: 614933, title: 'Atlas', poster_path: '/bcM2Tl5HlsvPBnL8DKP9Ie6vU4r.jpg', vote_average: 6.3, release_date: '2024-05-24', genre_ids: [28, 12, 878] },
  { id: 653346, title: 'Kingdom of the Planet of the Apes', poster_path: '/gKkl37BQuKTanygYQG1pyYgLVgf.jpg', vote_average: 7.0, release_date: '2024-05-08', genre_ids: [878, 28, 12] },

  // ── Action ────────────────────────────────────────────────────────────────────
  { id: 299534, title: 'Avengers: Endgame', poster_path: '/or06FN3Dka5tukK1e9sl16pB3iy.jpg', vote_average: 8.4, release_date: '2019-04-24', genre_ids: [28, 12, 878] },
  { id: 157336, title: 'Interstellar', poster_path: '/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg', vote_average: 8.4, release_date: '2014-11-05', genre_ids: [28, 12, 878, 18] },
  { id: 475557, title: 'Joker', poster_path: '/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg', vote_average: 8.2, release_date: '2019-10-02', genre_ids: [80, 18, 53] },
  { id: 315162, title: 'Puss in Boots: The Last Wish', poster_path: '/kuf6dutpsT0vSVehic3EZIqkOBt.jpg', vote_average: 8.0, release_date: '2022-12-07', genre_ids: [16, 35, 12] },
  { id: 361743, title: 'Top Gun: Maverick', poster_path: '/62HCnUTziyWcpDaBO2i1DX17ljH.jpg', vote_average: 8.3, release_date: '2022-05-24', genre_ids: [28, 18] },
  { id: 324857, title: 'Spider-Man: Into the Spider-Verse', poster_path: '/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg', vote_average: 8.4, release_date: '2018-12-14', genre_ids: [16, 28, 12, 878] },
  { id: 522627, title: 'The Suicide Squad', poster_path: '/kb4s0ML0iVZlG6wAKbbs9NAm6X.jpg', vote_average: 7.6, release_date: '2021-07-28', genre_ids: [28, 35, 878] },
  { id: 399566, title: 'Godzilla vs. Kong', poster_path: '/pgqgaUx1cJb5oZQQ5v0tNARCeBp.jpg', vote_average: 7.5, release_date: '2021-03-24', genre_ids: [28, 878, 12] },
  { id: 338952, title: 'Fantastic Beasts: The Crimes of Grindelwald', poster_path: '/ld7YB9vBRp1GM9o17vWZ7an27Z6.jpg', vote_average: 6.8, release_date: '2018-11-14', genre_ids: [12, 14, 878] },
  { id: 438631, title: 'Dune', poster_path: '/d5NXSklpcvkOrg9ssjFUYber1u.jpg', vote_average: 7.8, release_date: '2021-10-22', genre_ids: [878, 12] },

  // ── Comedy ────────────────────────────────────────────────────────────────────
  { id: 98, title: 'Gladiator', poster_path: '/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg', vote_average: 7.9, release_date: '2000-05-05', genre_ids: [28, 18] },
  { id: 10625, title: 'Mean Girls', poster_path: '/5mP8F0NYSVrwrlWRCSD5nTSSBGi.jpg', vote_average: 7.2, release_date: '2004-04-30', genre_ids: [35, 18] },
  { id: 9880, title: '50 First Dates', poster_path: '/6L0pBNXQW8PnE7gLXECmRxhW6LJ.jpg', vote_average: 6.9, release_date: '2004-02-13', genre_ids: [35, 10749, 18] },
  { id: 23168, title: 'The Proposal', poster_path: '/ggFHVNu6YYI5L9pCfOacjizRGt.jpg', vote_average: 6.9, release_date: '2009-06-19', genre_ids: [35, 10749] },
  { id: 65754, title: 'The Grand Budapest Hotel', poster_path: '/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg', vote_average: 8.1, release_date: '2014-02-26', genre_ids: [35, 80] },
  { id: 218, title: 'The Truman Show', poster_path: '/vuza0WqY239yBXOadKlGwJsZJFE.jpg', vote_average: 8.2, release_date: '1998-06-05', genre_ids: [35, 18] },
  { id: 38757, title: 'The Secret in Their Eyes', poster_path: '/2E0dhlGEgMHB9ESGE1L5HH9BKZF.jpg', vote_average: 8.0, release_date: '2009-08-13', genre_ids: [80, 18, 53] },
  { id: 218778, title: 'About Time', poster_path: '/1ziSCpDMUGCr5HoTqJlT5l99fYq.jpg', vote_average: 7.9, release_date: '2013-09-04', genre_ids: [35, 18, 10749] },
  { id: 11977, title: 'Hitch', poster_path: '/bZbkpCo4WNOI1TGDSmz2ATXESVS.jpg', vote_average: 7.0, release_date: '2005-02-11', genre_ids: [35, 10749] },
  { id: 862, title: 'Toy Story', poster_path: '/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg', vote_average: 8.3, release_date: '1995-10-30', genre_ids: [16, 35, 12, 10751] },

  // ── Drama ─────────────────────────────────────────────────────────────────────
  { id: 901362, title: 'Trolls Band Together', poster_path: '/bkpPTZUdq31UGDovmszsg2CchiI.jpg', vote_average: 7.2, release_date: '2023-10-20', genre_ids: [16, 35, 10402, 10751, 12] },
  { id: 315162, title: 'A Beautiful Mind', poster_path: '/zwzWCmH72OSC9NA0ipoqynmS7Vg.jpg', vote_average: 7.9, release_date: '2001-12-13', genre_ids: [18] },
  { id: 194, title: 'Amélie', poster_path: '/o0dtvmNvKXkadpuCxlMwdIrXOdl.jpg', vote_average: 8.0, release_date: '2001-04-25', genre_ids: [35, 10749, 18] },
  { id: 77338, title: 'The Intouchables', poster_path: '/1edBABkBwHkxjKiHQf4UNpkTGN3.jpg', vote_average: 8.3, release_date: '2011-11-02', genre_ids: [35, 18] },
  { id: 19995, title: 'Avatar', poster_path: '/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg', vote_average: 7.6, release_date: '2009-12-15', genre_ids: [28, 12, 14, 878] },
  { id: 10681, title: 'WALL·E', poster_path: '/hbhFnRzzg6ZDmm8YAmxBnQpQIPh.jpg', vote_average: 8.4, release_date: '2008-06-22', genre_ids: [16, 12, 878] },
  { id: 101, title: 'Leon: The Professional', poster_path: '/yI6X2cCM5YPJtxMhUd3dPGqDAhw.jpg', vote_average: 8.3, release_date: '1994-09-14', genre_ids: [28, 80, 18] },
  { id: 637, title: 'Requiem for a Dream', poster_path: '/nOd6vjEmzCT0k4VYqsA2hwyi87C.jpg', vote_average: 8.0, release_date: '2000-10-06', genre_ids: [18] },
  { id: 8587, title: 'The Lion King', poster_path: '/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg', vote_average: 8.3, release_date: '1994-06-15', genre_ids: [16, 10751, 18] },
  { id: 240, title: 'The Godfather Part II', poster_path: '/hek3koDUyRQk7FIhPXsa6mT2Zc3.jpg', vote_average: 8.6, release_date: '1974-12-18', genre_ids: [18, 80] },

  // ── Horror ────────────────────────────────────────────────────────────────────
  { id: 346364, title: 'It', poster_path: '/9E2y5Q7WlCVNnhAef4nF6J1OBkg.jpg', vote_average: 7.3, release_date: '2017-09-05', genre_ids: [27, 18] },
  { id: 420818, title: 'It Chapter Two', poster_path: '/v6ToJcRDvgqPMuRolFArUaIBzxq.jpg', vote_average: 6.8, release_date: '2019-09-04', genre_ids: [27, 18] },
  { id: 456165, title: 'Hereditary', poster_path: '/4O1m7LkG4OA0TA60SYqnqGFseBD.jpg', vote_average: 7.3, release_date: '2018-06-08', genre_ids: [27, 18, 9648] },
  { id: 458156, title: 'Joker (2019)', poster_path: '/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg', vote_average: 8.2, release_date: '2019-10-02', genre_ids: [80, 18, 53] },
  { id: 374720, title: 'Dunkirk', poster_path: '/ebSnODDg9lbsMIaWg2uAbjn7TO5.jpg', vote_average: 7.8, release_date: '2017-07-19', genre_ids: [28, 18, 36, 10752] },
  { id: 419430, title: 'Get Out', poster_path: '/fS0UYXD7KHGqOVJYBGGSBnrYRtV.jpg', vote_average: 7.7, release_date: '2017-02-24', genre_ids: [27, 9648, 53] },
  { id: 9552, title: 'A Nightmare on Elm Street', poster_path: '/prKphFLQ8PvGFe2fMJREXEqU3hh.jpg', vote_average: 7.4, release_date: '1984-11-16', genre_ids: [27, 53] },
  { id: 694, title: 'The Shining', poster_path: '/nRj5511mZdTl8hKvjJLoWEioRCj.jpg', vote_average: 8.4, release_date: '1980-05-23', genre_ids: [18, 27, 9648] },
  { id: 185, title: 'Halloween', poster_path: '/qVykxM4Gg2TXzDOnTvz2W8WPdxs.jpg', vote_average: 7.7, release_date: '1978-10-25', genre_ids: [27, 53] },
  { id: 493922, title: 'Hereditary', poster_path: '/bHMFJHRg7lBhL6LVcIrHfRqf0cP.jpg', vote_average: 7.3, release_date: '2018-06-08', genre_ids: [27, 18] },

  // ── Romance ────────────────────────────────────────────────────────────────────
  { id: 376867, title: 'Moonlight', poster_path: '/lSGoKaTVNpcrDP0yZKdj4RJmSji.jpg', vote_average: 7.4, release_date: '2016-10-21', genre_ids: [18] },
  { id: 8321, title: 'In Bruges', poster_path: '/6AMBWMtE8kLI6Nnzwvbm4L7xm50.jpg', vote_average: 7.9, release_date: '2008-02-08', genre_ids: [80, 35, 18] },
  { id: 289, title: 'The Notebook', poster_path: '/rNzQyW4f8B8cQeg7Dgj3n6eT5k9.jpg', vote_average: 7.9, release_date: '2004-06-25', genre_ids: [18, 10749] },
  { id: 10529, title: 'Pride & Prejudice', poster_path: '/wMmph8UPouFtbSRmKb8QrZhfMSD.jpg', vote_average: 7.8, release_date: '2005-09-16', genre_ids: [18, 10749] },
  { id: 397422, title: 'The Shape of Water', poster_path: '/k4FwHlMhuRR5BISY2Gm2QZHlH5Q.jpg', vote_average: 7.4, release_date: '2017-12-01', genre_ids: [18, 14, 53, 10749] },
  { id: 493, title: 'Eternal Sunshine of the Spotless Mind', poster_path: '/5MwkWH9tYHv3mV9OdYTMR5qreIz.jpg', vote_average: 8.2, release_date: '2004-03-19', genre_ids: [878, 10749, 18] },
  { id: 286217, title: 'The Martian', poster_path: '/5BHuvQ6p9kfc091Z8RiFNhCwL4b.jpg', vote_average: 7.8, release_date: '2015-10-02', genre_ids: [28, 18, 878] },
  { id: 18785, title: 'The Notebook', poster_path: '/wy2LfhImY2s9YHPxaApfFZ4DXMM.jpg', vote_average: 7.9, release_date: '2004-06-25', genre_ids: [18, 10749] },
  { id: 597, title: 'Titanic', poster_path: '/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg', vote_average: 7.9, release_date: '1997-11-18', genre_ids: [18, 10749] },
  { id: 10691, title: 'Twilight', poster_path: '/a6lnYzuFJKXFDuiHrODRDM0pP5j.jpg', vote_average: 6.7, release_date: '2008-11-21', genre_ids: [14, 18, 10749] },

  // ── Sci-Fi ────────────────────────────────────────────────────────────────────
  { id: 11324, title: 'Shutter Island', poster_path: '/kve20tXwUZpu4GUX8l6X7Z3oDko.jpg', vote_average: 8.2, release_date: '2010-02-13', genre_ids: [18, 9648, 53] },
  { id: 568124, title: 'Encanto', poster_path: '/4j0PNHkMr5ax3IA8tjtxcmPU3QT.jpg', vote_average: 7.7, release_date: '2021-11-24', genre_ids: [16, 35, 14, 10751, 10402] },
  { id: 10138, title: 'Iron Man', poster_path: '/78lPtwv72eTNqFW9COBF8l0mkXy.jpg', vote_average: 7.9, release_date: '2008-04-30', genre_ids: [28, 12, 878] },
  { id: 284054, title: 'Black Panther', poster_path: '/uxzzxijgPIY7slzFvMotPv8wjKA.jpg', vote_average: 7.4, release_date: '2018-02-13', genre_ids: [28, 12, 878] },
  { id: 335984, title: 'Blade Runner 2049', poster_path: '/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg', vote_average: 8.0, release_date: '2017-10-04', genre_ids: [878, 18] },
  { id: 49026, title: 'The Dark Knight Rises', poster_path: '/hr0L2aueqlP2BYUblTTjmtn1lAF.jpg', vote_average: 8.4, release_date: '2012-07-16', genre_ids: [28, 80, 18, 53] },
  { id: 38, title: 'Eternal Sunshine', poster_path: '/5MwkWH9tYHv3mV9OdYTMR5qreIz.jpg', vote_average: 8.2, release_date: '2004-03-19', genre_ids: [878, 18, 10749] },
  { id: 374720, title: 'Ex Machina', poster_path: '/4YhGp6cFXQjkdE7WZFZVTnE2DIi.jpg', vote_average: 7.7, release_date: '2015-01-21', genre_ids: [18, 878, 53] },
  { id: 1771, title: 'Captain America: The First Avenger', poster_path: '/vSNFBMCBQNUcKENF1nE3k2NxXp2.jpg', vote_average: 7.0, release_date: '2011-07-22', genre_ids: [28, 12, 878] },
  { id: 293660, title: 'Deadpool', poster_path: '/fSRb7vyIP8rQpL0I47P3qUsEKX3.jpg', vote_average: 8.0, release_date: '2016-02-09', genre_ids: [28, 35, 878] },

  // ── Animation ─────────────────────────────────────────────────────────────────
  { id: 37799, title: 'The Social Network', poster_path: '/n0ybibhJtQ5icDqTp8eRytcIHso.jpg', vote_average: 7.7, release_date: '2010-09-24', genre_ids: [18] },
  { id: 140607, title: 'Star Wars: The Force Awakens', poster_path: '/wqnLdwVXoBjKibFRR5U3y0aDUhs.jpg', vote_average: 7.9, release_date: '2015-12-15', genre_ids: [28, 12, 878] },
  { id: 218, title: 'How to Train Your Dragon', poster_path: '/cycling7Th84Ov1c5j80BjFkknv3.jpg', vote_average: 7.9, release_date: '2010-03-26', genre_ids: [16, 12, 35, 14, 10751] },
  { id: 812, title: 'Aladdin', poster_path: '/xBHvZcjRiWyobQ9kxBhO6B2dtRI.jpg', vote_average: 7.9, release_date: '1992-11-25', genre_ids: [16, 12, 14, 35, 10749, 10751] },
  { id: 10193, title: 'Toy Story 3', poster_path: '/AbbXspMOwdvwWZgVn0kh5XkGI3d.jpg', vote_average: 8.3, release_date: '2010-06-18', genre_ids: [16, 35, 12, 10751] },
  { id: 9806, title: 'The Incredibles', poster_path: '/2LqaLgk4Z226KkgPJuiOQ58VRLE.jpg', vote_average: 7.9, release_date: '2004-10-27', genre_ids: [16, 28, 12, 35, 10751] },
  { id: 149532, title: 'Frozen', poster_path: '/iJldESHdAsh6Y5pGT3cl0bHFkzP.jpg', vote_average: 7.4, release_date: '2013-11-19', genre_ids: [16, 35, 14, 10749, 10751, 10402] },
  { id: 301528, title: 'Toy Story 4', poster_path: '/w9kR8qbmQ01HwnvK4alvnQ2ca0L.jpg', vote_average: 7.8, release_date: '2019-06-19', genre_ids: [16, 35, 12, 10751] },
  { id: 68718, title: 'Django Unchained', poster_path: '/7oWY8VDWW7thTzWh3OKYRkWcKRL.jpg', vote_average: 8.4, release_date: '2012-12-25', genre_ids: [18, 37] },
  { id: 423108, title: 'Coco', poster_path: '/eKi8dIrr8voobbaGzDpe8w0PVbC.jpg', vote_average: 8.3, release_date: '2017-10-27', genre_ids: [16, 35, 14, 10751, 10402] },
]

// Distribute into categories
export const SAMPLE_ROWS = {
  trending:    SAMPLE_MOVIES.slice(0, 20),
  topRated:    SAMPLE_MOVIES.slice(20, 30),
  popular:     SAMPLE_MOVIES.slice(30, 40),
  upcoming:    SAMPLE_MOVIES.slice(40, 50),
  action:      SAMPLE_MOVIES.slice(50, 60),
  comedy:      SAMPLE_MOVIES.slice(60, 70),
  drama:       SAMPLE_MOVIES.slice(70, 80),
  horror:      SAMPLE_MOVIES.slice(80, 90),
  romance:     SAMPLE_MOVIES.slice(90, 100),
  scifi:       SAMPLE_MOVIES.slice(100, 110),
  animation:   SAMPLE_MOVIES.slice(110, 120),
  thriller:    [...SAMPLE_MOVIES.slice(82, 90), ...SAMPLE_MOVIES.slice(0, 5)],
  fantasy:     [...SAMPLE_MOVIES.slice(17, 22), ...SAMPLE_MOVIES.slice(60, 65)],
  crime:       [...SAMPLE_MOVIES.slice(4, 8), ...SAMPLE_MOVIES.slice(76, 82)],
  family:      [...SAMPLE_MOVIES.slice(13, 18), ...SAMPLE_MOVIES.slice(110, 116)],
  nowPlaying:  SAMPLE_MOVIES.slice(5, 20),
}
